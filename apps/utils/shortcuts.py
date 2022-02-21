from datetime import datetime
from geopy.distance import geodesic
from django.shortcuts import _get_queryset
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except ObjectDoesNotExist:
        return None


def filter_kwargs_builder(uuid, date):
    date = datetime.strptime(date, '%Y-%m-%d')
    return {
        'user__uuid': uuid,
        'created_at__day': date.day,
        'created_at__month': date.month,
        'created_at__year': date.year
    }


def convert_to_datetime(dt):
    return datetime.strptime(dt, '%d/%m/%y %H:%M:%S')


def get_datetime_now_str():
    return datetime.now().strftime('%d/%m/%y %H:%M:%S')


def get_point(location):
    latitude, longitude = get_coordinates(location)
    point = (latitude, longitude)
    return point


def get_point_instance(point):
    return Point(
        point.get('longitude'),
        point.get('latitude')
    )


def get_coordinates(location):
    return location.get('latitude'), location.get('longitude')


def calc_distance(point_a, point_b):
    return geodesic(point_a, point_b)


def calc_speed(distance, time):
    total = distance / time
    return round(total, 2)


def get_difference_in_hours(time_a, time_b):
    time = (time_a - time_b).total_seconds()
    return time / 3600

