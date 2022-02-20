import json
from datetime import datetime
from geopy.distance import geodesic
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString, Point

from apps.utils.models import BaseModel, BaseModelUser
from apps.utils.redis import client as redis
from apps.utils.shortcuts import get_object_or_none, filter_kwargs_builder


class CompanyUser(BaseModelUser, User):
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

    def last_location_processor(self, current_location):
        last_location = redis.get_json(self.location_redis_key)
        if bool(last_location):
            if self.get_current_visit().get('visit_id'):
                self.last_visit_processor(current_location)

            current_latitude = current_location.get('latitude')
            current_longitude = current_location.get('longitude')
            current_point = (current_latitude, current_longitude)

            last_latitude = last_location.get('latitude')
            last_longitude = last_location.get('longitude')
            last_point = (last_latitude, last_longitude)

            distance = geodesic(last_point, current_point)

            displacement = redis.get_setup().get('displacement')

            if distance.m >= displacement:
                current_time_str = current_location.get('time')
                current_time = datetime.strptime(current_time_str, '%d/%m/%y %H:%M:%S')

                last_time_str = last_location.get('time')
                last_time = datetime.strptime(last_time_str, '%d/%m/%y %H:%M:%S')

                time = (current_time - last_time).total_seconds() / 3600

                speed_limit = redis.get_setup().get('speed_limit')
                speed = round(distance.km / time, 2)

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
        else:
            current_route = {
                'points': []
            }
            self.set_current_route(current_route)

    def store_location_in_route(self, current_location):
        from .tasks import setup_visits

        current_route = self.get_current_route()
        current_route['points'].append(current_location)
        self.set_current_route(current_route)

        latitude = current_location.get('latitude')
        longitude = current_location.get('longitude')
        setup_visits.delay(self.id, latitude, longitude)

    def route_processor(self, visit_id):
        current_route = self.get_current_route()
        points = []
        speeds = 0
        speeds_collector = []
        for point in current_route.get('points'):
            location = Point(
                point.get('longitude'),
                point.get('latitude')
            )
            points.append(location)

            speed = point.get('speed')
            if speed is not None:
                speeds_collector.append(speed)
                speeds += speed

        line_str = LineString(points)

        speed_avg = speeds / len(points)

        speeds_collector.sort(reverse=True)
        max_speed = speeds_collector[0]

        SpeedReport.objects.create(
            user=self,
            location_start=points[0],
            location_end=points[-1],
            route=line_str,
            history=current_route,
            speed_avg=speed_avg,
            max_speed=max_speed
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
            time_finish_str = current_location.get('time')
            time_finish = datetime.strptime(time_finish_str, '%d/%m/%y %H:%M:%S')
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
