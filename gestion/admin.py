from django.contrib import admin
from .models import *

class ReportStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'color')
admin.site.register(ReportStatus, ReportStatusAdmin)

class InsuranceCompAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(InsuranceComp, InsuranceCompAdmin)

class AssociationAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Association, AssociationAdmin)

