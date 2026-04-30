import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduling_system.settings')
django.setup()

from shifts.models import Employee, ShiftType, SchedulingRule

# Create shift types
ShiftType.objects.get_or_create(name='Day Shift', color='#4CAF50', is_work_shift=True)
ShiftType.objects.get_or_create(name='Night Shift', color='#FF9800', is_work_shift=True)
ShiftType.objects.get_or_create(name='Off', color='#F44336', is_work_shift=False)
ShiftType.objects.get_or_create(name='Cleaning', color='#9C27B0', is_work_shift=False)

# Create employees
Employee.objects.get_or_create(
    name='John Doe',
    email='john@example.com',
    hire_date=date.today(),
    is_active=True
)
Employee.objects.get_or_create(
    name='Jane Smith',
    email='jane@example.com',
    hire_date=date.today(),
    is_active=True
)
Employee.objects.get_or_create(
    name='Bob Johnson',
    email='bob@example.com',
    hire_date=date.today(),
    is_active=True
)

# Create rule
SchedulingRule.objects.get_or_create(
    name='Standard Rule',
    max_consecutive_days=5,
    mandatory_rest_days=1,
    avoid_consecutive_nights=True
)

print("Sample data created.")