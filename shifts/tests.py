from datetime import date, timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .exceptions import ValidationError
from .models import Employee, Schedule, SchedulingRule, ShiftType
from .services import ScheduleService, SchedulingService


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class EmployeeModelTest(TestCase):
    def _make(self, **kwargs):
        defaults = {"name": "Alice", "email": "alice@test.com", "hire_date": date.today()}
        defaults.update(kwargs)
        return Employee.objects.create(**defaults)

    def test_str(self):
        emp = self._make()
        self.assertEqual(str(emp), "Alice")

    def test_is_active_default(self):
        emp = self._make()
        self.assertTrue(emp.is_active)

    def test_timestamps_set_on_create(self):
        emp = self._make()
        self.assertIsNotNone(emp.created_at)
        self.assertIsNotNone(emp.updated_at)

    def test_unique_email(self):
        self._make()
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Employee.objects.create(name="Bob", email="alice@test.com", hire_date=date.today())


class ShiftTypeModelTest(TestCase):
    def test_str(self):
        st = ShiftType(name="Dia")
        self.assertEqual(str(st), "Dia")

    def test_invalid_hex_color_raises(self):
        st = ShiftType(name="Teste", color="notacolor", is_work_shift=True)
        with self.assertRaises(DjangoValidationError):
            st.full_clean()

    def test_valid_hex_color(self):
        st = ShiftType(name="Dia", color="#4CAF50", is_work_shift=True)
        st.full_clean()  # should not raise


class ScheduleModelTest(TestCase):
    def setUp(self):
        self.emp = Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        self.shift = ShiftType.objects.create(name="Dia", color="#00ff00", is_work_shift=True)

    def test_str(self):
        s = Schedule(employee=self.emp, date=date.today(), shift_type=self.shift)
        self.assertIn("Alice", str(s))

    def test_timestamps_set_on_create(self):
        s = Schedule.objects.create(employee=self.emp, date=date.today(), shift_type=self.shift)
        self.assertIsNotNone(s.created_at)

    def test_unique_employee_date(self):
        Schedule.objects.create(employee=self.emp, date=date.today(), shift_type=self.shift)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Schedule.objects.create(employee=self.emp, date=date.today(), shift_type=self.shift)


class SchedulingRuleModelTest(TestCase):
    def test_str(self):
        rule = SchedulingRule(name="Padrão")
        self.assertEqual(str(rule), "Padrão")

    def test_default_values(self):
        rule = SchedulingRule.objects.create(name="Teste")
        self.assertEqual(rule.max_consecutive_days, 5)
        self.assertEqual(rule.mandatory_rest_days, 1)
        self.assertEqual(rule.min_employees_per_day, 1)
        self.assertEqual(rule.max_schedule_days, 90)
        self.assertEqual(rule.solver_time_limit_seconds, 30)


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class ScheduleServiceTest(TestCase):
    def setUp(self):
        self.emp = Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        self.shift = ShiftType.objects.create(name="Dia", color="#00ff00", is_work_shift=True)

    def test_update_shift_creates_new(self):
        today = date.today()
        schedule = ScheduleService.update_shift(self.emp.id, today, self.shift.id)
        self.assertEqual(schedule.employee, self.emp)
        self.assertEqual(schedule.shift_type, self.shift)
        self.assertEqual(Schedule.objects.count(), 1)

    def test_update_shift_updates_existing(self):
        today = date.today()
        Schedule.objects.create(employee=self.emp, date=today, shift_type=self.shift)
        new_shift = ShiftType.objects.create(name="Noite", color="#ff0000", is_work_shift=True)
        schedule = ScheduleService.update_shift(self.emp.id, today, new_shift.id)
        self.assertEqual(schedule.shift_type, new_shift)
        self.assertEqual(Schedule.objects.count(), 1)

    def test_update_shift_invalid_employee(self):
        with self.assertRaises(ValidationError):
            ScheduleService.update_shift(9999, date.today(), self.shift.id)

    def test_update_shift_invalid_shift_type(self):
        with self.assertRaises(ValidationError):
            ScheduleService.update_shift(self.emp.id, date.today(), 9999)

    def test_validate_generation_start_after_end(self):
        start = date.today()
        end = start - timedelta(days=1)
        with self.assertRaises(ValidationError):
            ScheduleService.validate_schedule_generation(start, end, [])

    def test_validate_generation_invalid_employee_ids(self):
        with self.assertRaises(ValidationError):
            ScheduleService.validate_schedule_generation(date.today(), date.today(), [9999])

    def test_get_calendar_data_empty(self):
        today = date.today()
        events = ScheduleService.get_calendar_data(today, today)
        self.assertEqual(events, [])

    def test_get_calendar_data_with_schedule(self):
        today = date.today()
        Schedule.objects.create(employee=self.emp, date=today, shift_type=self.shift)
        events = ScheduleService.get_calendar_data(today, today)
        self.assertEqual(len(events), 1)
        self.assertIn("Alice", events[0]["title"])

    def test_export_schedule_data_empty(self):
        today = date.today()
        data, dates = ScheduleService.export_schedule_data(today, today)
        self.assertEqual(data, [])
        self.assertEqual(dates, [])


class SchedulingServiceTest(TestCase):
    def setUp(self):
        self.rule = SchedulingRule.objects.create(
            name="Teste",
            max_consecutive_days=5,
            mandatory_rest_days=1,
            avoid_consecutive_nights=False,
            min_employees_per_day=1,
            solver_time_limit_seconds=10,
        )
        ShiftType.objects.create(name="Dia", color="#00ff00", is_work_shift=True)
        ShiftType.objects.create(name="Folga", color="#cccccc", is_work_shift=False)
        self.emp1 = Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        self.emp2 = Employee.objects.create(name="Bob", email="b@t.com", hire_date=date.today())

    def test_generate_schedule_creates_records(self):
        start = date.today()
        end = start + timedelta(days=6)
        svc = SchedulingService(rule_id=self.rule.id)
        count = svc.generate_schedule(start, end)
        self.assertGreater(count, 0)
        self.assertEqual(Schedule.objects.count(), count)

    def test_generate_schedule_no_employees_raises(self):
        Employee.objects.all().update(is_active=False)
        svc = SchedulingService(rule_id=self.rule.id)
        with self.assertRaises(ValidationError):
            svc.generate_schedule(date.today(), date.today() + timedelta(days=6))

    def test_generate_schedule_exceeds_max_days(self):
        self.rule.max_schedule_days = 3
        self.rule.save()
        svc = SchedulingService(rule_id=self.rule.id)
        with self.assertRaises(ValidationError):
            svc.generate_schedule(date.today(), date.today() + timedelta(days=10))

    def test_invalid_rule_id_raises(self):
        with self.assertRaises(ValidationError):
            SchedulingService(rule_id=9999)


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------

class EmployeeAPITest(APITestCase):
    def test_list_employees(self):
        Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        r = self.client.get("/api/employees/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_create_employee(self):
        payload = {"name": "Bob", "email": "b@t.com", "hire_date": str(date.today()), "is_active": True}
        r = self.client.post("/api/employees/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)

    def test_create_employee_duplicate_email(self):
        Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        payload = {"name": "Alice2", "email": "a@t.com", "hire_date": str(date.today()), "is_active": True}
        r = self.client.post("/api/employees/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_active_employees(self):
        Employee.objects.create(name="Active", email="act@t.com", hire_date=date.today(), is_active=True)
        Employee.objects.create(name="Inactive", email="inact@t.com", hire_date=date.today(), is_active=False)
        r = self.client.get("/api/employees/?is_active=true")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        names = [e["name"] for e in r.data["results"]]
        self.assertIn("Active", names)
        self.assertNotIn("Inactive", names)


class ShiftTypeAPITest(APITestCase):
    def test_create_shift_type_valid(self):
        payload = {"name": "Dia", "color": "#4CAF50", "is_work_shift": True}
        r = self.client.post("/api/shift-types/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_shift_type_invalid_color(self):
        payload = {"name": "Erro", "color": "notacolor", "is_work_shift": True}
        r = self.client.post("/api/shift-types/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class GenerateScheduleAPITest(APITestCase):
    def setUp(self):
        ShiftType.objects.create(name="Dia", color="#00ff00", is_work_shift=True)
        ShiftType.objects.create(name="Folga", color="#cccccc", is_work_shift=False)
        Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        Employee.objects.create(name="Bob", email="b@t.com", hire_date=date.today())
        SchedulingRule.objects.create(
            name="Teste", max_consecutive_days=5, mandatory_rest_days=1,
            avoid_consecutive_nights=False, solver_time_limit_seconds=10,
        )

    def test_generate_success(self):
        start = date.today()
        end = start + timedelta(days=6)
        r = self.client.post(
            "/api/schedules/generate/",
            {"start_date": str(start), "end_date": str(end)},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("schedules_created", r.data)

    def test_generate_start_after_end(self):
        start = date.today()
        r = self.client.post(
            "/api/schedules/generate/",
            {"start_date": str(start), "end_date": str(start - timedelta(days=1))},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_range_too_large(self):
        start = date.today()
        end = start + timedelta(days=400)
        r = self.client.post(
            "/api/schedules/generate/",
            {"start_date": str(start), "end_date": str(end)},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class ExportAPITest(APITestCase):
    def test_export_no_data_returns_404(self):
        today = date.today()
        r = self.client.get(f"/api/export/?start={today}&end={today}")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_missing_params(self):
        r = self.client.get("/api/export/")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_with_data(self):
        emp = Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        shift = ShiftType.objects.create(name="Dia", color="#00ff00", is_work_shift=True)
        today = date.today()
        Schedule.objects.create(employee=emp, date=today, shift_type=shift)
        r = self.client.get(f"/api/export/?start={today}&end={today}")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("spreadsheet", r["Content-Type"])


class UpdateShiftAPITest(APITestCase):
    def setUp(self):
        self.emp = Employee.objects.create(name="Alice", email="a@t.com", hire_date=date.today())
        self.shift = ShiftType.objects.create(name="Dia", color="#00ff00", is_work_shift=True)

    def test_update_shift_creates(self):
        payload = {
            "employee_id": self.emp.id,
            "date": str(date.today()),
            "shift_type_id": self.shift.id,
        }
        r = self.client.post("/api/update-shift/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(Schedule.objects.count(), 1)

    def test_update_shift_invalid_employee(self):
        payload = {"employee_id": 9999, "date": str(date.today()), "shift_type_id": self.shift.id}
        r = self.client.post("/api/update-shift/", payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
