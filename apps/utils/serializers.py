from rest_framework import serializers


class DateFilterSerializer(serializers.Serializer):
    date = serializers.DateField(format='%Y-%m-%d')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

