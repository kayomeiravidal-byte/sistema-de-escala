import django.db.models.deletion
import django.utils.timezone
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shifts", "0001_initial"),
    ]

    operations = [
        # Employee: created_at / updated_at
        migrations.AddField(
            model_name="employee",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="employee",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # Employee: ordering meta (no field changes, just meta)
        migrations.AlterModelOptions(
            name="employee",
            options={
                "ordering": ["name"],
                "verbose_name": "Funcionário",
                "verbose_name_plural": "Funcionários",
            },
        ),
        # ShiftType: add hex validator + meta
        migrations.AlterField(
            model_name="shifttype",
            name="color",
            field=models.CharField(
                default="#ffffff",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        regex=r"^#[0-9A-Fa-f]{6}$",
                        message="Cor hexadecimal inválida (ex: #FF5733).",
                    )
                ],
            ),
        ),
        migrations.AlterModelOptions(
            name="shifttype",
            options={
                "ordering": ["name"],
                "verbose_name": "Tipo de Turno",
                "verbose_name_plural": "Tipos de Turno",
            },
        ),
        # Schedule: created_at / updated_at + indexes + meta
        migrations.AddField(
            model_name="schedule",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="schedule",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name="schedule",
            options={
                "ordering": ["-date", "employee__name"],
                "verbose_name": "Escala",
                "verbose_name_plural": "Escalas",
            },
        ),
        migrations.AddIndex(
            model_name="schedule",
            index=models.Index(fields=["date"], name="shifts_sche_date_idx"),
        ),
        migrations.AddIndex(
            model_name="schedule",
            index=models.Index(fields=["employee", "date"], name="shifts_sche_emp_date_idx"),
        ),
        # SchedulingRule: new fields + meta
        migrations.AddField(
            model_name="schedulingrule",
            name="min_employees_per_day",
            field=models.PositiveIntegerField(
                default=1,
                validators=[django.core.validators.MinValueValidator(1)],
                help_text="Mínimo de funcionários trabalhando em cada dia.",
            ),
        ),
        migrations.AddField(
            model_name="schedulingrule",
            name="max_schedule_days",
            field=models.PositiveIntegerField(
                default=90,
                validators=[django.core.validators.MinValueValidator(1)],
                help_text="Limite máximo de dias em uma geração de escala.",
            ),
        ),
        migrations.AddField(
            model_name="schedulingrule",
            name="solver_time_limit_seconds",
            field=models.PositiveIntegerField(
                default=30,
                validators=[django.core.validators.MinValueValidator(5)],
                help_text="Tempo máximo em segundos para o solver OR-Tools.",
            ),
        ),
        migrations.AlterModelOptions(
            name="schedulingrule",
            options={
                "ordering": ["name"],
                "verbose_name": "Regra de Escalonamento",
                "verbose_name_plural": "Regras de Escalonamento",
            },
        ),
    ]
