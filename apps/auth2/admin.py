from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from leaflet.admin import LeafletGeoAdmin

from .forms import CompanyUserAdminForm
from .models import CompanyUser, SpeedReport


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = [
        'uuid',
        'username',
        'date_joined',
        'is_active',
        'deleted'
    ]
    list_display_links = [
        'uuid'
    ]
    form = CompanyUserAdminForm


@admin.register(SpeedReport)
class SpeedReportAdmin(LeafletGeoAdmin):
    list_display = [
        'uuid',
        'user',
        'created_at',
    ]
    list_filter = [
        'user'
    ]
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

