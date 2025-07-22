from django.urls import path
from pwa import views


urlpatterns = [
    path('', views.index, name="pwa-home"),
    path('home/', views.index, name="pwa-home"),
    path('login/', views.pin_login, name="pwa-login"),
    path('logoff/', views.pin_logout, name="pwa-logout"),

    # EMPLOYEES
    path('employee/', views.employee_home, name="pwa-employee"),
    path('employee/report/<int:obj_id>/', views.employee_report, name="pwa-employee-report"),
    path('employee/report/new/', views.employee_report_new, name="pwa-employee-report-new"),
    path('employee/report/new/<int:obj_id>/', views.employee_report_new, name="pwa-employee-report-new"),
    path('employee/report/new/save/', views.employee_report_new_save, name="pwa-employee-report-new-save"),
    path('employee/report/save/', views.employee_report_save, name="pwa-employee-report-save"),
    path('employee/report/img/save/', views.employee_report_img_save, name="pwa-employee-report-img-save"),
    path('employee/report/img/remove/', views.employee_report_img_remove, name="pwa-employee-report-img-remove"),
    path('employee/notes/', views.employee_notes, name="pwa-employee-notes"),
    path('employee/note/', views.employee_note, name="pwa-employee-note"),
    path('employee/note/save/', views.employee_note_save, name="pwa-employee-note-save"),
]

