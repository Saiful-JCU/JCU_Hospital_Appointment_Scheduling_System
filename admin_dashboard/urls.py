from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard_home, name='admin_dashboard_home'),


    path('departments/', views.department_list, name='admin_department_list'),
    path('departments/add/', views.department_add, name='admin_department_add'),
    path('departments/<int:pk>/edit/', views.department_edit, name='admin_department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='admin_department_delete'),


    path('doctors/', views.doctor_list, name='admin_doctor_list'),
    path('doctors/add/', views.doctor_add, name='admin_doctor_add'),
    path('doctors/<int:doctor_id>/edit/', views.doctor_edit, name='admin_doctor_edit'),
    path('doctors/<int:doctor_id>/delete/', views.doctor_delete, name='admin_doctor_delete'),

    path('patients/', views.patient_list, name='admin_patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='admin_patient_detail'),
    path('patients/<int:patient_id>/delete/', views.patient_delete, name='admin_patient_delete'),


    path('reports/', views.report_dashboard, name='admin_report_dashboard'),
    path('reports/appointments/day/', views.appointments_per_day_report, name='appointments_per_day_report'),
    path('reports/appointments/week/', views.appointments_per_week_report, name='appointments_per_week_report'),
    path('reports/patient-flow/', views.daily_patient_flow_report, name='daily_patient_flow_report'),
]