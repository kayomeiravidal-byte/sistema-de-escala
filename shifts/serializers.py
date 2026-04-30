from rest_framework import serializers
from .models import Employee, ShiftType, Schedule, SchedulingRule

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class ShiftTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftType
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    shift_type_name = serializers.CharField(source='shift_type.name', read_only=True)
    shift_color = serializers.CharField(source='shift_type.color', read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'

class SchedulingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulingRule
        fields = '__all__'

# Response serializers for specific endpoints
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
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    rule_id = serializers.IntegerField(required=False)

class ShiftUpdateRequestSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    date = serializers.DateField()
    shift_type_id = serializers.IntegerField()

class ExportRequestSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()