from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Employee, ShiftType, Schedule
from .serializers import (
    EmployeeSerializer, ShiftTypeSerializer, ScheduleSerializer,
    ScheduleGenerationRequestSerializer, ShiftUpdateRequestSerializer,
    ExportRequestSerializer
)
from .exceptions import ValidationError, OptimizationError, DataAccessError
from .services import SchedulingService, ScheduleService
import pandas as pd

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ShiftTypeViewSet(viewsets.ModelViewSet):
    queryset = ShiftType.objects.all()
    serializer_class = ShiftTypeSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        """Override create to use service validation"""
        try:
            # Validate through service
            employee_id = request.data.get('employee')
            date = request.data.get('date')
            shift_type_id = request.data.get('shift_type')

            if not all([employee_id, date, shift_type_id]):
                return Response({'error': 'All fields required'}, status=status.HTTP_400_BAD_REQUEST)

            schedule = ScheduleService.update_shift(employee_id, date, shift_type_id)
            serializer = self.get_serializer(schedule)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DataAccessError as e:
            return Response({'error': f'Data access error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Override update to use service"""
        try:
            instance = self.get_object()
            employee_id = request.data.get('employee', instance.employee_id)
            date = request.data.get('date', instance.date)
            shift_type_id = request.data.get('shift_type', instance.shift_type_id)

            schedule = ScheduleService.update_shift(employee_id, date, shift_type_id)
            serializer = self.get_serializer(schedule)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DataAccessError as e:
            return Response({'error': f'Data access error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_schedule(request):
    """Generate optimized schedule using scheduling service"""
    serializer = ScheduleGenerationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        start, end, employees = ScheduleService.validate_schedule_generation(
            data['start_date'], data['end_date'], data.get('employee_ids', [])
        )

        service = SchedulingService(data.get('rule_id'))
        service.generate_schedule(start, end, employees)

        return Response({'message': 'Schedule generated successfully'})
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except OptimizationError as e:
        return Response({'error': f'Optimization failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_calendar_data(request):
    """Get schedule data for calendar display"""
    serializer = ExportRequestSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        employee_ids = request.query_params.getlist('employee_ids')

        events = ScheduleService.get_calendar_data(data['start'], data['end'], employee_ids)
        return Response(events)
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_shift(request):
    """Update a single shift assignment"""
    serializer = ShiftUpdateRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        schedule = ScheduleService.update_shift(data['employee_id'], data['date'], data['shift_type_id'])
        response_serializer = ScheduleSerializer(schedule)
        return Response(response_serializer.data)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except DataAccessError as e:
        return Response({'error': f'Data access error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def export_schedule(request):
    """Export schedule to Excel"""
    serializer = ExportRequestSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        df_data = ScheduleService.export_schedule_data(data['start'], data['end'])
        df = pd.DataFrame(df_data)

        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=schedule.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Schedule', index=False)

        return response
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Frontend view
def calendar_view(request):
    employees = Employee.objects.all()
    shift_types = ShiftType.objects.all()
    return render(request, 'shifts/calendar.html', {
        'employees': employees,
        'shift_types': shift_types,
    })
