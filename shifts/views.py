import logging

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .exceptions import DataAccessError, OptimizationError, ValidationError
from .models import Employee, Schedule, SchedulingRule, ShiftType
from .serializers import (
    EmployeeSerializer,
    ExportRequestSerializer,
    ScheduleGenerationRequestSerializer,
    ScheduleSerializer,
    SchedulingRuleSerializer,
    ShiftTypeSerializer,
    ShiftUpdateRequestSerializer,
)
from .services import ScheduleService, SchedulingService

logger = logging.getLogger(__name__)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filterset_fields = ["is_active"]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "hire_date", "created_at"]


class ShiftTypeViewSet(viewsets.ModelViewSet):
    queryset = ShiftType.objects.all()
    serializer_class = ShiftTypeSerializer
    filterset_fields = ["is_work_shift"]
    search_fields = ["name"]


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related("employee", "shift_type").all()
    serializer_class = ScheduleSerializer
    filterset_fields = ["employee", "shift_type", "date"]
    search_fields = ["employee__name"]
    ordering_fields = ["date", "employee__name"]

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        date = request.data.get("date")
        shift_type_id = request.data.get("shift_type")

        if not all([employee_id, date, shift_type_id]):
            return Response(
                {"error": "Os campos employee, date e shift_type são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            schedule = ScheduleService.update_shift(employee_id, date, shift_type_id)
            return Response(
                self.get_serializer(schedule).data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Erro inesperado ao criar escala.")
            return Response(
                {"error": "Erro interno do servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        employee_id = request.data.get("employee", instance.employee_id)
        date = request.data.get("date", str(instance.date))
        shift_type_id = request.data.get("shift_type", instance.shift_type_id)

        try:
            schedule = ScheduleService.update_shift(employee_id, date, shift_type_id)
            return Response(self.get_serializer(schedule).data)
        except ValidationError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Erro inesperado ao atualizar escala.")
            return Response(
                {"error": "Erro interno do servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SchedulingRuleViewSet(viewsets.ModelViewSet):
    queryset = SchedulingRule.objects.all()
    serializer_class = SchedulingRuleSerializer
    search_fields = ["name"]


@api_view(["POST"])
def generate_schedule(request):
    serializer = ScheduleGenerationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        start, end, employees = ScheduleService.validate_schedule_generation(
            data["start_date"], data["end_date"], data.get("employee_ids") or []
        )
        service = SchedulingService(data.get("rule_id"))
        count = service.generate_schedule(start, end, employees)
        return Response(
            {"message": "Escala gerada com sucesso.", "schedules_created": count},
            status=status.HTTP_200_OK,
        )
    except ValidationError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except OptimizationError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception:
        logger.exception("Erro inesperado ao gerar escala.")
        return Response(
            {"error": "Erro interno do servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_calendar_data(request):
    serializer = ExportRequestSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        employee_ids = request.query_params.getlist("employee_ids") or None
        events = ScheduleService.get_calendar_data(data["start"], data["end"], employee_ids)
        return Response(events)
    except Exception:
        logger.exception("Erro ao buscar dados de calendário.")
        return Response(
            {"error": "Erro interno do servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def update_shift(request):
    serializer = ShiftUpdateRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        schedule = ScheduleService.update_shift(data["employee_id"], data["date"], data["shift_type_id"])
        return Response(ScheduleSerializer(schedule).data)
    except ValidationError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception("Erro ao atualizar turno.")
        return Response(
            {"error": "Erro interno do servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def export_schedule(request):
    serializer = ExportRequestSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        schedule_data, _ = ScheduleService.export_schedule_data(data["start"], data["end"])

        if not schedule_data:
            return Response(
                {"error": "Nenhum dado encontrado no período informado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        df = pd.DataFrame(schedule_data)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="escala_{data["start"]}_{data["end"]}.xlsx"'
        )
        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Escala", index=False)

        return response
    except Exception:
        logger.exception("Erro ao exportar escala.")
        return Response(
            {"error": "Erro ao gerar o arquivo Excel."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def calendar_view(request):
    employees = Employee.objects.filter(is_active=True).order_by("name")
    shift_types = ShiftType.objects.all().order_by("name")
    rules = SchedulingRule.objects.all()
    return render(request, "shifts/calendar.html", {
        "employees": employees,
        "shift_types": shift_types,
        "rules": rules,
    })
