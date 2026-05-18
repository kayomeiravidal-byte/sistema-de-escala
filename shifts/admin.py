from django.contrib import admin

from .models import Employee, Schedule, SchedulingRule, ShiftType

admin.site.site_header = "Sistema de Escalonamento"
admin.site.site_title = "Escalonamento Admin"
admin.site.index_title = "Painel de Administração"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_active", "hire_date", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "email")
    ordering = ("name",)
    date_hierarchy = "hire_date"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "email", "is_active", "hire_date")}),
        ("Auditoria", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ShiftType)
class ShiftTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "color_preview", "is_work_shift")
    list_filter = ("is_work_shift",)
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Cor")
    def color_preview(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<span style="background:{};padding:2px 12px;border-radius:3px;">&nbsp;</span> {}',
            obj.color,
            obj.color,
        )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "shift_type", "created_at")
    list_filter = ("shift_type", "date", "employee__is_active")
    search_fields = ("employee__name", "shift_type__name")
    ordering = ("-date", "employee__name")
    date_hierarchy = "date"
    autocomplete_fields = ("employee", "shift_type")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("employee", "date", "shift_type")}),
        ("Auditoria", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("employee", "shift_type")


@admin.register(SchedulingRule)
class SchedulingRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "max_consecutive_days",
        "mandatory_rest_days",
        "min_employees_per_day",
        "max_schedule_days",
        "solver_time_limit_seconds",
        "avoid_consecutive_nights",
    )
    search_fields = ("name",)
    fieldsets = (
        ("Identificação", {"fields": ("name",)}),
        (
            "Regras de Trabalho",
            {
                "fields": (
                    "max_consecutive_days",
                    "mandatory_rest_days",
                    "avoid_consecutive_nights",
                    "min_employees_per_day",
                )
            },
        ),
        (
            "Limites de Geração",
            {"fields": ("max_schedule_days", "solver_time_limit_seconds")},
        ),
    )
