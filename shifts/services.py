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
                raise ValidationError(f"SchedulingRule with id={rule_id} not found")
        else:
            self.rule = SchedulingRule.objects.first() or SchedulingRule.objects.create(
                name="Default Rule",
                max_consecutive_days=5,
                mandatory_rest_days=1,
                avoid_consecutive_nights=True
            )

    def generate_schedule(self, start_date, end_date, employees=None):
        logger.info(f"Generating schedule from {start_date} to {end_date}")
        if employees is None:
            employees = Employee.objects.filter(is_active=True)

        employees = list(employees)
        shift_types = list(ShiftType.objects.all())

        # Clear existing schedules in the range for regeneration
        Schedule.objects.filter(
            date__range=(start_date, end_date),
            employee__in=employees
        ).delete()

        # Use OR-Tools for optimization
        self._optimize_schedule(start_date, end_date, employees, shift_types)

    def _optimize_schedule(self, start_date, end_date, employees, shift_types):
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()

        # Create date list
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)

        # Variables: x[emp_id][date_idx][shift_id] = 1 if assigned
        x = {}
        work_vars = {}  # work_vars[emp_id][date_idx] = 1 if work shift
        for emp in employees:
            work_vars[emp.id] = []
            for date_idx, date in enumerate(dates):
                work = model.NewBoolVar(f'work_{emp.id}_{date_idx}')
                work_vars[emp.id].append(work)
                for shift in shift_types:
                    x[(emp.id, date_idx, shift.id)] = model.NewBoolVar(f'x_{emp.id}_{date_idx}_{shift.id}')
                # Exactly one shift per day
                model.Add(sum(x[(emp.id, date_idx, s.id)] for s in shift_types) == 1)
                # Work indicator
                work_shifts = [s for s in shift_types if s.is_work_shift]
                model.Add(work == sum(x[(emp.id, date_idx, s.id)] for s in work_shifts))

        # Constraints

        # Max consecutive work days
        for emp in employees:
            for i in range(len(dates) - self.rule.max_consecutive_days):
                window = work_vars[emp.id][i:i + self.rule.max_consecutive_days + 1]
                model.Add(sum(window) <= self.rule.max_consecutive_days)

        # Mandatory rest: simplified - after max consecutive work, next day off
        for emp in employees:
            for i in range(len(dates) - self.rule.max_consecutive_days - self.rule.mandatory_rest_days):
                consecutive_work = work_vars[emp.id][i:i + self.rule.max_consecutive_days]
                rest_days = work_vars[emp.id][i + self.rule.max_consecutive_days:i + self.rule.max_consecutive_days + self.rule.mandatory_rest_days]
                # If all consecutive are work, then all rest must be off
                all_work = model.NewBoolVar(f'all_work_{emp.id}_{i}')
                model.Add(sum(consecutive_work) == self.rule.max_consecutive_days).OnlyEnforceIf(all_work)
                model.Add(sum(consecutive_work) < self.rule.max_consecutive_days).OnlyEnforceIf(all_work.Not())
                model.Add(sum(rest_days) == 0).OnlyEnforceIf(all_work)

        # Minimum work shifts per day (at least 1)
        for date_idx in range(len(dates)):
            model.Add(sum(work_vars[emp.id][date_idx] for emp in employees) >= 1)

        # Avoid consecutive nights
        if self.rule.avoid_consecutive_nights:
            night_shift = next((s for s in shift_types if 'night' in s.name.lower()), None)
            if night_shift:
                for emp in employees:
                    for i in range(1, len(dates)):
                        model.Add(x[(emp.id, i, night_shift.id)] + x[(emp.id, i-1, night_shift.id)] <= 1)

        # Objective: minimize variance in total work days
        total_work = []
        for emp in employees:
            total = model.NewIntVar(0, len(dates), f'total_{emp.id}')
            model.Add(total == sum(work_vars[emp.id]))
            total_work.append(total)

        min_work = model.NewIntVar(0, len(dates), 'min_work')
        max_work = model.NewIntVar(0, len(dates), 'max_work')
        model.AddMinEquality(min_work, total_work)
        model.AddMaxEquality(max_work, total_work)
        model.Minimize(max_work - min_work)

        # Solve
        status = solver.Solve(model)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            # Create schedules
            for emp in employees:
                for date_idx, date in enumerate(dates):
                    for shift in shift_types:
                        if solver.Value(x[(emp.id, date_idx, shift.id)]):
                            Schedule.objects.create(
                                employee=emp,
                                date=date,
                                shift_type=shift
                            )
                            break
            variance = solver.Value(max_work) - solver.Value(min_work)
            logger.info(f"Solution found with variance: {variance}")
        else:
            logger.warning("No feasible solution found")
            raise OptimizationError("Solver could not find a feasible schedule for the given constraints")

    def update_shift(self, employee_id, date, shift_type_id):
        with transaction.atomic():
            schedule, created = Schedule.objects.get_or_create(
                employee_id=employee_id,
                date=date,
                defaults={'shift_type_id': shift_type_id}
            )
            if not created:
                schedule.shift_type_id = shift_type_id
                schedule.save()
            return schedule


class ScheduleService:
    @staticmethod
    def get_calendar_data(start_date, end_date, employee_ids=None):
        """Get schedule data formatted for calendar display"""
        logger.debug(f"Fetching calendar data from {start_date} to {end_date}")
        schedules = Schedule.objects.filter(
            date__range=(start_date, end_date)
        ).select_related('employee', 'shift_type')

        if employee_ids:
            schedules = schedules.filter(employee_id__in=employee_ids)

        events = []
        for schedule in schedules:
            events.append({
                'id': schedule.id,
                'title': f"{schedule.employee.name}: {schedule.shift_type.name}",
                'start': str(schedule.date),
                'backgroundColor': schedule.shift_type.color,
                'extendedProps': {
                    'employee_id': schedule.employee.id,
                    'shift_type_id': schedule.shift_type.id,
                }
            })
        logger.debug(f"Returning {len(events)} calendar events")
        return events

    @staticmethod
    def export_schedule_data(start_date, end_date):
        """Get schedule data formatted for Excel export"""
        schedules = Schedule.objects.filter(
            date__range=(start_date, end_date)
        ).select_related('employee', 'shift_type').order_by('employee__name', 'date')

        # Create DataFrame
        data = []
        employees = {}
        dates = set()

        for sched in schedules:
            emp_name = sched.employee.name
            date_str = str(sched.date)
            shift_name = sched.shift_type.name

            if emp_name not in employees:
                employees[emp_name] = {}
            employees[emp_name][date_str] = shift_name
            dates.add(date_str)

        dates = sorted(list(dates))

        for emp_name in sorted(employees.keys()):
            row = {'Employee': emp_name}
            for date in dates:
                row[date] = employees[emp_name].get(date, 'Off')
            data.append(row)

        return data

    @staticmethod
    def update_shift(employee_id, date, shift_type_id):
        """Update or create a shift assignment"""
        logger.info(f"Updating shift for employee {employee_id} on {date} to shift {shift_type_id}")
        with transaction.atomic():
            # Validate inputs
            try:
                employee = Employee.objects.get(id=employee_id)
                shift_type = ShiftType.objects.get(id=shift_type_id)
            except (Employee.DoesNotExist, ShiftType.DoesNotExist) as e:
                logger.error(f"Validation error: {e}")
                raise ValidationError("Invalid employee or shift type")

            schedule, created = Schedule.objects.get_or_create(
                employee=employee,
                date=date,
                defaults={'shift_type': shift_type}
            )
            if not created:
                schedule.shift_type = shift_type
                schedule.save()
            logger.info(f"Shift {'created' if created else 'updated'} successfully")
            return schedule

    @staticmethod
    def validate_schedule_generation(start_date, end_date, employee_ids):
        """Validate inputs for schedule generation"""
        from datetime import date as date_type
        if not start_date or not end_date:
            raise ValidationError("start_date and end_date are required")

        if isinstance(start_date, str):
            try:
                start_date = datetime.fromisoformat(start_date).date()
                end_date = datetime.fromisoformat(end_date).date()
            except ValueError:
                raise ValidationError("Invalid date format")

        if start_date > end_date:
            raise ValidationError("start_date must be before end_date")

        if employee_ids:
            employees = Employee.objects.filter(id__in=employee_ids, is_active=True)
            if len(employees) != len(employee_ids):
                raise ValidationError("Some employees not found or inactive")
        else:
            employees = Employee.objects.filter(is_active=True)

        return start_date, end_date, employees