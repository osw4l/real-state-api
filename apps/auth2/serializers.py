from django.contrib.auth import authenticate
from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import CompanyUser, SpeedReport
from apps.utils.shortcuts import get_object_or_none


class UserLoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    username = serializers.CharField(min_length=2, max_length=64)
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError({
                'error': 'Invalid Credentials'
            })
        if not hasattr(user, 'companyuser'):
            raise serializers.ValidationError({
                'error': 'You do not have enough permissions to enter here'
            })
        self.context['user'] = user
        return data

    def create(self, data):
        user = self.context['user']
        token = get_object_or_none(Token, user=user)
        if token:
            token.delete()
        token, created = Token.objects.update_or_create(user=user)
        user = CompanyUserSerializer(user.companyuser)
        return user.data, token.key


class CompanyUserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = CompanyUser
        fields = (
            'uuid',
            'username',
            'full_name'
        )


class LocationSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class SpeedReportSerializer(serializers.ModelSerializer):
    location_start = PointField()
    location_end = PointField()
    speeding = serializers.ReadOnlyField()

    class Meta:
        model = SpeedReport
        fields = (
            'uuid',
            'location_start',
            'location_end',
            'speed_avg',
            'max_speed',
            'route',
            'speeding'
        )
