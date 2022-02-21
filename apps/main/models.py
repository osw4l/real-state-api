import json
import math

from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.utils.models import BaseModel
from django_lifecycle import LifecycleModel, AFTER_CREATE, BEFORE_UPDATE, hook
from apps.utils.redis import client as redis
from apps.utils.shortcuts import filter_kwargs_builder


class Setup(BaseModel):
    speed_limit = models.PositiveIntegerField(
        default=50,
        validators=[
            MinValueValidator(40),
            MaxValueValidator(80)
        ]
    )
    displacement = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(10),
            MaxValueValidator(500)
        ]
    )

    class Meta:
        verbose_name = 'Setup'
        verbose_name_plural = 'Setup'

    def __str__(self):
        return 'Project Setup'

    def save(self, *args, **kwargs):
        if self.__class__.objects.all().count() <= 1:
            super().save(*args, **kwargs)

    def get_data(self):
        return json.dumps({
            'displacement': self.displacement,
            'speed_limit': self.speed_limit
        })

    @hook(AFTER_CREATE)
    def on_create(self):
        redis.set('setup', self.get_data())

    @hook(BEFORE_UPDATE)
    def on_update(self):
        redis.set('setup', self.get_data())


class Property(BaseModel):
    address = models.CharField(
        max_length=50
    )
    location = models.PointField()

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.address


class Visit(BaseModel):
    user = models.ForeignKey(
        'auth2.CompanyUser',
        on_delete=models.CASCADE,
        related_name='visits'
    )
    property = models.ForeignKey(
        'main.Property',
        on_delete=models.CASCADE
    )
    end_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'

    @classmethod
    def filter_by_date_and_user(cls, user_uuid, date):
        kwargs = filter_kwargs_builder(uuid=user_uuid, date=date)
        return cls.objects.filter(**kwargs)

    def done(self, time_finish):
        self.end_at = time_finish
        self.save(update_fields=['end_at'])

    def duration(self):
        result = None
        if self.end_at:
            diff = self.end_at - self.created_at
            s_to_m = round(diff.total_seconds() / 60)
            minutes = math.ceil(s_to_m)
            result = f'{minutes} Minutes approx'
        return result
