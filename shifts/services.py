from datetime import datetime, timedelta
from django.db import transaction
from .models import Employee, ShiftType, Schedule, SchedulingRule
from ortools.sat.python import cp_model
from .exceptions import ValidationError, OptimizationError, DataAccessError
import logging

logger = logging.getLogger(__name__)


class SchedulingService:
    def __init__(self, rule_id=None):
        if rule_id:
            try:
                self.rule = SchedulingRule.objects.get(id=rule_id)
            except SchedulingRule.DoesNotExist:
                raise ValidationError(f"Regra de escalonamento id={rule_id} não encontrada.")
        else:
            self.rule = SchedulingRule.objects.first() or SchedulingRule.objects.create(
                name="Regra Padrão",
                max_consecutive_days=5,
                mandatory_rest_days=1,
                avoid_consecutive_nights=True,
            )

    @transaction.atomic
    def generate_schedule(self, start_date, end_date, employees=None):
        logger.info("Gerando escala de %s a %s", start_date, end_date)

        delta = (end_date - start_date).days + 1
        if delta > self.rule.max_schedule_days:
            raise ValidationError(
                f"O intervalo solicitado ({delta} dias) excede o limite da regra "
                f"({self.rule.max_schedule_days} dias)."
            )

        if employees is None:
            employees = list(Employee.objects.filter(is_active=True))
        else:
            employees = list(employees)

        if not employees:
            raise ValidationError("Nenhum funcionário ativo encontrado para gerar a escala.")

        shift_types = list(ShiftType.objects.all())
        if not shift_types:
            raise ValidationError("Nenhum tipo de turno cadastrado.")

        Schedule.objects.filter(
            date__range=(start_date, end_date),
            employee__in=employees,
        ).delete()

        schedules = self._optimize_schedule(start_date, end_date, employees, shift_types)
        Schedule.objects.bulk_create(schedules, ignore_conflicts=False)
        logger.info("Escala gerada: %d registros criados.", len(schedules))
        return len(schedules)

    def _optimize_schedule(self, start_date, end_date, employees, shift_types):
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.rule.solver_time_limit_seconds

        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)

        n_dates = len(dates)
        max_consec = self.rule.max_consecutive_days
        min_per_day = self.rule.min_employees_per_day

        # Variables: x[(emp_id, date_idx, shift_id)] = 1 if assigned
        x = {}
        work_vars = {}
        for emp in employees:
            work_vars[emp.id] = []
            for date_idx in range(n_dates):
                work = model.NewBoolVar(f"work_{emp.id}_{date_idx}")
                work_vars[emp.id].append(work)
                for shift in shift_types:
                    x[(emp.id, date_idx, shift.id)] = model.NewBoolVar(
                        f"x_{emp.id}_{date_idx}_{shift.id}"
                    )
                # Exactly one shift per employee per day
                model.Add(sum(x[(emp.id, date_idx, s.id)] for s in shift_types) == 1)
                # work indicator = sum of is_work_shift slots
                work_shifts = [s for s in shift_types if s.is_work_shift]
                model.Add(work == sum(x[(emp.id, date_idx, s.id)] for s in work_shifts))

        # Max consecutive work days (sliding window)
        for emp in employees:
            for i in range(n_dates - max_consec):
                window = work_vars[emp.id][i : i + max_consec + 1]
                model.Add(sum(window) <= max_consec)

        # Mandatory rest after max consecutive work
        rest = self.rule.mandatory_rest_days
        for emp in employees:
            for i in range(n_dates - max_consec - rest):
                consecutive_work = work_vars[emp.id][i : i + max_consec]
                rest_days = work_vars[emp.id][i + max_consec : i + max_consec + rest]
                all_work = model.NewBoolVar(f"all_work_{emp.id}_{i}")
                model.Add(sum(consecutive_work) == max_consec).OnlyEnforceIf(all_work)
                model.Add(sum(consecutive_work) < max_consec).OnlyEnforceIf(all_work.Not())
                model.Add(sum(rest_days) == 0).OnlyEnforceIf(all_work)

        # Minimum employees working each day
        for date_idx in range(n_dates):
            model.Add(
                sum(work_vars[emp.id][date_idx] for emp in employees) >= min_per_day
            )

        # Avoid consecutive night shifts
        if self.rule.avoid_consecutive_nights:
            night_shift = next(
                (s for s in shift_types if "noite" in s.name.lower() or "night" in s.name.lower()),
                None,
            )
            if night_shift:
                for emp in employees:
                    for i in range(1, n_dates):
                        model.Add(
                            x[(emp.id, i, night_shift.id)]
                            + x[(emp.id, i - 1, night_shift.id)]
                            <= 1
                        )

        # Objective: minimize spread of total work days across employees
        total_work = []
        for emp in employees:
            total = model.NewIntVar(0, n_dates, f"total_{emp.id}")
            model.Add(total == sum(work_vars[emp.id]))
            total_work.append(total)

        min_work = model.NewIntVar(0, n_dates, "min_work")
        max_work = model.NewIntVar(0, n_dates, "max_work")
        model.AddMinEquality(min_work, total_work)
        model.AddMaxEquality(max_work, total_work)
        model.Minimize(max_work - min_work)

        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            logger.warning("Solver sem solução viável. Status: %s", solver.StatusName(status))
            raise OptimizationError(
                "O solver não encontrou uma escala viável para as restrições configuradas. "
                "Tente ampliar o período, reduzir restrições ou aumentar o timeout."
            )

        variance = solver.Value(max_work) - solver.Value(min_work)
        logger.info(
            "Solução encontrada (status=%s, variância=%d).",
            solver.StatusName(status),
            variance,
        )

        schedules = []
        for emp in employees:
            for date_idx, date in enumerate(dates):
                for shift in shift_types:
                    if solver.Value(x[(emp.id, date_idx, shift.id)]):
                        schedules.append(
                            Schedule(employee=emp, date=date, shift_type=shift)
                        )
                        break

        return schedules


class ScheduleService:
    @staticmethod
    def get_calendar_data(start_date, end_date, employee_ids=None):
        logger.debug("Buscando dados de calendário de %s a %s", start_date, end_date)
        qs = (
            Schedule.objects.filter(date__range=(start_date, end_date))
            .select_related("employee", "shift_type")
            .order_by("date", "employee__name")
        )
        if employee_ids:
            qs = qs.filter(employee_id__in=employee_ids)

        events = [
            {
                "id": s.id,
                "title": f"{s.employee.name}: {s.shift_type.name}",
                "start": str(s.date),
                "backgroundColor": s.shift_type.color,
                "extendedProps": {
                    "employee_id": s.employee.id,
                    "shift_type_id": s.shift_type.id,
                },
            }
            for s in qs
        ]
        logger.debug("Retornando %d eventos.", len(events))
        return events

    @staticmethod
    def export_schedule_data(start_date, end_date):
        qs = (
            Schedule.objects.filter(date__range=(start_date, end_date))
            .select_related("employee", "shift_type")
            .order_by("employee__name", "date")
        )

        employees: dict = {}
        dates: set = set()

        for sched in qs:
            emp_name = sched.employee.name
            date_str = str(sched.date)
            if emp_name not in employees:
                employees[emp_name] = {}
            employees[emp_name][date_str] = sched.shift_type.name
            dates.add(date_str)

        sorted_dates = sorted(dates)
        data = []
        for emp_name in sorted(employees.keys()):
            row = {"Funcionário": emp_name}
            for d in sorted_dates:
                row[d] = employees[emp_name].get(d, "Folga")
            data.append(row)

        return data, sorted_dates

    @staticmethod
    @transaction.atomic
    def update_shift(employee_id, date, shift_type_id):
        logger.info(
            "Atualizando turno: funcionário=%s, data=%s, turno=%s",
            employee_id, date, shift_type_id,
        )
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise ValidationError(f"Funcionário id={employee_id} não encontrado.")

        try:
            shift_type = ShiftType.objects.get(id=shift_type_id)
        except ShiftType.DoesNotExist:
            raise ValidationError(f"Tipo de turno id={shift_type_id} não encontrado.")

        schedule, created = Schedule.objects.get_or_create(
            employee=employee,
            date=date,
            defaults={"shift_type": shift_type},
        )
        if not created:
            schedule.shift_type = shift_type
            schedule.save(update_fields=["shift_type", "updated_at"])

        logger.info("Turno %s com sucesso.", "criado" if created else "atualizado")
        return schedule

    @staticmethod
    def validate_schedule_generation(start_date, end_date, employee_ids):
        if not start_date or not end_date:
            raise ValidationError("start_date e end_date são obrigatórios.")

        if isinstance(start_date, str):
            try:
                start_date = datetime.fromisoformat(start_date).date()
                end_date = datetime.fromisoformat(end_date).date()
            except ValueError:
                raise ValidationError("Formato de data inválido. Use YYYY-MM-DD.")

        if start_date > end_date:
            raise ValidationError("start_date deve ser anterior a end_date.")

        if employee_ids:
            active_ids = set(
                Employee.objects.filter(id__in=employee_ids, is_active=True).values_list("id", flat=True)
            )
            missing = set(employee_ids) - active_ids
            if missing:
                raise ValidationError(
                    f"Funcionários não encontrados ou inativos: {sorted(missing)}."
                )
            employees = Employee.objects.filter(id__in=employee_ids, is_active=True)
        else:
            employees = Employee.objects.filter(is_active=True)

        return start_date, end_date, employees
