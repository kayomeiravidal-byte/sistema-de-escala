from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet)
router.register(r'shift-types', views.ShiftTypeViewSet)
router.register(r'schedules', views.ScheduleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schedules/generate/', views.generate_schedule, name='generate_schedule'),
    path('api/schedules/calendar_data/', views.get_calendar_data, name='calendar_data'),
    path('api/update-shift/', views.update_shift, name='update_shift'),
    path('api/export/', views.export_schedule, name='export_schedule'),
    path('calendar/', views.calendar_view, name='calendar'),
]