import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduling_system.settings')
django.setup()

from shifts.models import Employee, ShiftType, SchedulingRule

# Tipos de turno
ShiftType.objects.get_or_create(name='Turno Diurno',  defaults={'color': '#4CAF50', 'is_work_shift': True})
ShiftType.objects.get_or_create(name='Turno Noturno', defaults={'color': '#FF9800', 'is_work_shift': True})
ShiftType.objects.get_or_create(name='Folga',         defaults={'color': '#F44336', 'is_work_shift': False})
ShiftType.objects.get_or_create(name='Limpeza',       defaults={'color': '#9C27B0', 'is_work_shift': False})

# Funcionários
Employee.objects.get_or_create(
    email='ana.silva@exemplo.com.br',
    defaults={'name': 'Ana Silva', 'hire_date': date(2022, 3, 15), 'is_active': True}
)
Employee.objects.get_or_create(
    email='carlos.souza@exemplo.com.br',
    defaults={'name': 'Carlos Souza', 'hire_date': date(2021, 7, 1), 'is_active': True}
)
Employee.objects.get_or_create(
    email='mariana.costa@exemplo.com.br',
    defaults={'name': 'Mariana Costa', 'hire_date': date(2023, 1, 10), 'is_active': True}
)
Employee.objects.get_or_create(
    email='rafael.lima@exemplo.com.br',
    defaults={'name': 'Rafael Lima', 'hire_date': date(2020, 11, 20), 'is_active': True}
)
Employee.objects.get_or_create(
    email='juliana.santos@exemplo.com.br',
    defaults={'name': 'Juliana Santos', 'hire_date': date(2022, 8, 5), 'is_active': True}
)

# Regra de escalonamento
SchedulingRule.objects.get_or_create(
    name='Regra Padrão',
    defaults={
        'max_consecutive_days': 5,
        'mandatory_rest_days': 2,
        'avoid_consecutive_nights': True,
        'min_employees_per_day': 2,
        'max_schedule_days': 90,
        'solver_time_limit_seconds': 30,
    }
)

print("Dados de exemplo criados com sucesso.")
