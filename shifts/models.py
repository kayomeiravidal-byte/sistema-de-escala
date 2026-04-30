from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField()

    def __str__(self):
        return self.name

class ShiftType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#ffffff')  # Hex color
    is_work_shift = models.BooleanField(default=True)  # True for work, False for off/cleaning

    def __str__(self):
        return self.name

class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.shift_type.name}"

class SchedulingRule(models.Model):
    name = models.CharField(max_length=100)
    max_consecutive_days = models.PositiveIntegerField(default=5)
    mandatory_rest_days = models.PositiveIntegerField(default=1)
    avoid_consecutive_nights = models.BooleanField(default=True)

    def __str__(self):
        return self.name
