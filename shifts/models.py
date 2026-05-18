import re
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


def validate_hex_color(value):
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError(f"'{value}' não é uma cor hexadecimal válida (ex: #FF5733).")


class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

    def __str__(self):
        return self.name


class ShiftType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#ffffff", validators=[validate_hex_color])
    is_work_shift = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tipo de Turno"
        verbose_name_plural = "Tipos de Turno"

    def __str__(self):
        return self.name


class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE, related_name="schedules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date", "employee__name"]
        verbose_name = "Escala"
        verbose_name_plural = "Escalas"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["employee", "date"]),
        ]

    def __str__(self):
        return f"{self.employee.name} — {self.date} — {self.shift_type.name}"


class SchedulingRule(models.Model):
    name = models.CharField(max_length=100)
    max_consecutive_days = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text="Máximo de dias consecutivos de trabalho permitidos.",
    )
    mandatory_rest_days = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Dias obrigatórios de descanso após atingir o máximo consecutivo.",
    )
    avoid_consecutive_nights = models.BooleanField(
        default=True,
        help_text="Evitar dois turnos noturnos seguidos para o mesmo funcionário.",
    )
    min_employees_per_day = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Mínimo de funcionários trabalhando em cada dia.",
    )
    max_schedule_days = models.PositiveIntegerField(
        default=90,
        validators=[MinValueValidator(1)],
        help_text="Limite máximo de dias em uma geração de escala.",
    )
    solver_time_limit_seconds = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(5)],
        help_text="Tempo máximo em segundos para o solver OR-Tools.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Regra de Escalonamento"
        verbose_name_plural = "Regras de Escalonamento"

    def __str__(self):
        return self.name
