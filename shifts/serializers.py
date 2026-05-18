import re
from rest_framework import serializers
from .models import Employee, ShiftType, Schedule, SchedulingRule


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "name", "email", "is_active", "hire_date", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ShiftTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftType
        fields = ["id", "name", "color", "is_work_shift"]

    def validate_color(self, value):
        if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
            raise serializers.ValidationError("Cor hexadecimal inválida. Use o formato #RRGGBB.")
        return value


class ScheduleSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    shift_type_name = serializers.CharField(source="shift_type.name", read_only=True)
    shift_color = serializers.CharField(source="shift_type.color", read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id", "employee", "employee_name",
            "date", "shift_type", "shift_type_name", "shift_color",
            "created_at", "updated_at",
        ]
        read_only_fields = ["employee_name", "shift_type_name", "shift_color", "created_at", "updated_at"]


class SchedulingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulingRule
        fields = [
            "id", "name",
            "max_consecutive_days", "mandatory_rest_days",
            "avoid_consecutive_nights",
            "min_employees_per_day", "max_schedule_days", "solver_time_limit_seconds",
        ]

    def validate(self, data):
        max_days = data.get("max_consecutive_days", getattr(self.instance, "max_consecutive_days", 5))
        rest_days = data.get("mandatory_rest_days", getattr(self.instance, "mandatory_rest_days", 1))
        if rest_days > max_days:
            raise serializers.ValidationError(
                "mandatory_rest_days não pode ser maior que max_consecutive_days."
            )
        return data


class CalendarEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    start = serializers.DateField()
    backgroundColor = serializers.CharField()
    extendedProps = serializers.DictField()


class ScheduleGenerationRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        default=list,
    )
    rule_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    def validate(self, data):
        start = data["start_date"]
        end = data["end_date"]
        if start > end:
            raise serializers.ValidationError("start_date deve ser anterior a end_date.")
        delta = (end - start).days + 1
        if delta > 366:
            raise serializers.ValidationError("O intervalo máximo de geração é 366 dias.")
        return data


class ShiftUpdateRequestSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    shift_type_id = serializers.IntegerField(min_value=1)


class ExportRequestSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()

    def validate(self, data):
        if data["start"] > data["end"]:
            raise serializers.ValidationError("'start' deve ser anterior a 'end'.")
        delta = (data["end"] - data["start"]).days + 1
        if delta > 366:
            raise serializers.ValidationError("O intervalo máximo de exportação é 366 dias.")
        return data
