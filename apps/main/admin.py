from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Setup, Property, Visit


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'displacement',
        'speed_limit'
    ]

    def has_add_permission(self, request):
        return Setup.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Property)
class PropertyAdmin(LeafletGeoAdmin):
    list_display = [
        'uuid',
        'address',
    ]
    search_fields = [
        'uuid',
        'address',
    ]


@admin.register(Visit)
class VisitAdmin(LeafletGeoAdmin):
    list_display = [
        'uuid',
        'user',
        'property',
        'created_at',
        'end_at',
        'duration'
    ]
    search_fields = [
        'user__first_name',
        'property__address',
    ]

    def has_add_permission(self, request):
        return False

