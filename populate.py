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
    email='john@example.com',
    defaults={'name': 'John Doe', 'hire_date': date.today(), 'is_active': True}
)
Employee.objects.get_or_create(
    email='jane@example.com',
    defaults={'name': 'Jane Smith', 'hire_date': date.today(), 'is_active': True}
)
Employee.objects.get_or_create(
    email='bob@example.com',
    defaults={'name': 'Bob Johnson', 'hire_date': date.today(), 'is_active': True}
)

# Create rule
SchedulingRule.objects.get_or_create(
    name='Standard Rule',
    max_consecutive_days=5,
    mandatory_rest_days=1,
    avoid_consecutive_nights=True
)

print("Sample data created.")