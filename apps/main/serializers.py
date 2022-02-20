from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from .models import Visit, Property
from ..auth2.serializers import CompanyUserSerializer


class PropertySerializer(serializers.ModelSerializer):
    location = PointField()

    class Meta:
        model = Property
        fields = (
            'uuid',
            'address',
            'location'
        )


class VisitSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    user = CompanyUserSerializer(read_only=True)
    duration = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    end_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')

    class Meta:
        model = Visit
        fields = (
            'uuid',
            'property',
            'user',
            'end_at',
            'created_at',
            'end_at',
            'duration'
        )


