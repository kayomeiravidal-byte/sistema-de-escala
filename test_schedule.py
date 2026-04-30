import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduling_system.settings')
django.setup()

from shifts.services import SchedulingService

# Test the scheduling
service = SchedulingService()
start = date.today()
end = start + timedelta(days=7)

print(f"Generating schedule from {start} to {end}")
service.generate_schedule(start, end)

# Print the schedule
from shifts.models import Schedule
schedules = Schedule.objects.filter(date__range=(start, end)).order_by('date', 'employee__name')
for sched in schedules:
    print(f"{sched.date}: {sched.employee.name} - {sched.shift_type.name}")