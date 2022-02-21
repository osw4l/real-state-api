import json
import uuid
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString
from apps.utils.models import BaseModel
from apps.utils.redis import client as redis
from apps.utils.shortcuts import (
    get_object_or_none,
    filter_kwargs_builder,
    convert_to_datetime,
    calc_distance,
    calc_speed,
    get_difference_in_hours,
    get_point,
    get_point_instance, get_coordinates
)


class CompanyUser(User):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    class Meta:
        verbose_name = 'Company User'
        verbose_name_plural = 'Company Users'

    @property
    def location_redis_key(self):
        return f'user_{self.id}_location'

    @property
    def route_redis_key(self):
        return f'user_{self.id}_route'

    @property
    def visit_redis_key(self):
        return f'user_{self.id}_visit'

    def get_current_route(self):
        return redis.get_json(self.route_redis_key)

    def set_current_route(self, value):
        return redis.set(self.route_redis_key, json.dumps(value))

    def get_current_visit(self):
        return redis.get_json(self.visit_redis_key)

    def set_current_visit(self, value):
        return redis.set(self.visit_redis_key, json.dumps(value))

    def delete_current_visit(self):
        return redis.delete(self.visit_redis_key)

    def store_current_location(self, location):
        current_location = location.copy()
        self.last_location_processor(current_location=current_location)
        redis.set(self.location_redis_key, json.dumps(location))
        return location

    def last_location_processor(self, current_location):
        last_location = redis.get_json(self.location_redis_key)
        if bool(last_location):
            if self.get_current_visit().get('visit_id'):
                self.last_visit_processor(current_location)

            last_point = get_point(last_location)
            current_point = get_point(current_location)
            distance = calc_distance(last_point, current_point)

            self.distance_processor(**{
                'distance': distance,
                'current_location': current_location,
                'last_location': last_location
            })
        else:
            current_route = {
                'points': [
                    current_location
                ]
            }
            self.set_current_route(current_route)

    def distance_processor(self, **kwargs):
        distance = kwargs.get('distance')
        current_location = kwargs.get('current_location')
        last_location = kwargs.get('last_location')

        speed_limit = redis.get_setup().get('speed_limit')
        if distance.m >= redis.get_setup().get('displacement'):
            current_time = convert_to_datetime(dt=current_location.get('time'))
            last_time = convert_to_datetime(dt=last_location.get('time'))

            time = get_difference_in_hours(current_time, last_time)
            speed = calc_speed(distance.km, time)
            current_location.update({
                'speed': speed,
                'distance': round(distance.meters, 2)
            })

            if speed > speed_limit:
                current_location.update({
                    'speed_alert': {
                        'current_limit': speed_limit,
                        'difference': round(speed - speed_limit, 2)
                    }
                })

            self.store_location_in_route(current_location=current_location)

    def store_location_in_route(self, current_location):
        from apps.main.tasks import setup_visits

        current_route = self.get_current_route()
        current_route['points'].append(current_location)
        self.set_current_route(current_route)

        latitude, longitude = get_coordinates(location=current_location)
        setup_visits.delay(self.id, latitude, longitude)

    def route_processor(self, visit_id):
        current_route = self.get_current_route()
        points = []
        speeds = 0
        speeds_collector = []
        for point in current_route.get('points'):
            location = get_point_instance(point=point)
            points.append(location)

            speed = point.get('speed')
            if speed is not None:
                speeds_collector.append(speed)
                speeds += speed

        speed_avg = speeds / len(points)
        speeds_collector.sort(reverse=True)

        SpeedReport.objects.create(
            user=self,
            location_start=points[0],
            location_end=points[-1],
            route=LineString(points),
            history=current_route,
            speed_avg=speed_avg,
            max_speed=speeds_collector[0]
        )

        current_route = {
            'points': []
        }

        self.set_current_route(current_route)
        self.set_current_visit({'visit_id': visit_id})

    def last_visit_processor(self, current_location):
        from apps.main.models import Visit
        last_visit_id = self.get_current_visit().get('visit_id')
        visit = get_object_or_none(Visit, id=last_visit_id)
        if visit:
            time_finish = convert_to_datetime(dt=current_location.get('time'))
            visit.done(time_finish=time_finish)
            self.delete_current_visit()


class SpeedReport(BaseModel):
    user = models.ForeignKey(
        'auth2.CompanyUser',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    location_start = models.PointField()
    location_end = models.PointField()
    route = models.LineStringField()
    speed_avg = models.PositiveIntegerField()
    max_speed = models.PositiveIntegerField()
    history = models.JSONField()

    class Meta:
        verbose_name = 'Speed Report'
        verbose_name_plural = 'Speed Reports'

    def __str__(self):
        return f'{self.uuid}'

    @classmethod
    def filter_by_date_and_user(cls, user_uuid, date):
        kwargs = filter_kwargs_builder(uuid=user_uuid, date=date)
        return cls.objects.filter(**kwargs)

    def speeding(self):
        speeds = []
        for item in self.history.get('points'):
            alert = item.get('speed_alert')
            if alert:
                speeds.append({
                    'speed': item.get('speed'),
                    'current_limit': alert.get('current_limit'),
                    'difference': alert.get('difference')
                })
        return speeds
