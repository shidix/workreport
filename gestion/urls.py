from django.urls import path
from . import views, auto_views

urlpatterns = [ 
    path('home', views.index, name='index'),
    path('reports/list', views.reports_list, name='reports-list'),
    path('reports/search', views.reports_search, name='reports-search'),
    path('reports/form', views.reports_form, name='reports-form'),
    path('reports/form-save', views.reports_form_save, name='reports-form-save'),
    path('reports/remove', views.reports_remove, name='reports-remove'),
    path('reports/imgs-download/<int:obj_id>', views.reports_imgs_download, name='reports-imgs-download'),

    #---------------------- NOTES -----------------------
    #path('notes', views.notes, name='notes'),
    path('notes/list', views.notes_list, name='notes-list'),
    path('notes/search', views.notes_search, name='notes-search'),
    path('notes/form', views.notes_form, name='notes-form'),
    path('notes/form-save', views.notes_form_save, name='notes-form-save'),
    path('notes/remove', views.notes_remove, name='notes-remove'),
    path('notes/remove-soft', views.notes_remove_soft, name='notes-remove-soft'),

    #---------------------- EMPLOYEES -----------------------
    path('employees', views.employees, name='employees'),
    path('employees/list', views.employees_list, name='employees-list'),
    path('employees/search', views.employees_search, name='employees-search'),
    path('employees/form', views.employees_form, name='employees-form'),
    path('employees/remove', views.employees_remove, name='employees-remove'),
    path('employees/save-email', views.employees_save_email, name='employees-save-email'),
    path('employees/export', views.employees_export, name='employees-export'),
    path('employees/import', views.employees_import, name='employees-import'),

    #------------------------- CLIENTS -----------------------
    path('clients', views.clients, name='clients'),
    path('clients/list', views.clients_list, name='clients-list'),
    path('clients/search', views.clients_search, name='clients-search'),
    path('clients/form', views.clients_form, name='clients-form'),
    path('clients/remove', views.clients_remove, name='clients-remove'),
    path('clients/print-all-qr', views.clients_print_all_qr, name='clients-print-all-qr'),
    path('clients/print-qr/<int:obj_id>', views.clients_print_qr, name='clients-print-qr'),
    path('clients/reports/<int:obj_id>', views.clients_reports, name='clients-reports'),

    #------------------------- SPEECH TO TEXT -----------------------
    path('set-note-concept', views.set_note_concept, name='set-note-concept'),

    #---------------------- AUTO -----------------------
    path('autosave_field/', auto_views.autosave_field, name='autosave_field'),
    path('autoremove_obj/', auto_views.autoremove_obj, name='autoremove_obj'),
]

