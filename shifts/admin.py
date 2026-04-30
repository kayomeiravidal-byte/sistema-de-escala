from django.contrib import admin
from .models import Employee, ShiftType, Schedule, SchedulingRule

admin.site.register(Employee)
admin.site.register(ShiftType)
admin.site.register(Schedule)
admin.site.register(SchedulingRule)
