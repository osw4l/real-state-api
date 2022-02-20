from celery import shared_task
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from .models import CompanyUser


@shared_task
def location_processor(user_id, data):
    location = {
        'longitude': float(data.get('longitude')),
        'latitude': float(data.get('latitude'))
    }

    user = CompanyUser.objects.filter(id=user_id)
    if user.exists():
        user.first().store_current_location(location=location)
        return {
            'location': location,
            'user_id': user_id
        }
    raise Exception({
        'user_error': f'user with id {user_id} does not exists'
    })


@shared_task
def setup_visits(user_id, latitude, longitude):
    from apps.main.models import Property, Visit
    user = CompanyUser.objects.filter(id=user_id)
    if user.exists():
        user = user.first()
        point = Point(longitude, latitude, srid=4326)
        properties = Property.objects.filter(
            location__distance_lte=(point, D(m=10))
        ).annotate(
            distance_m=Distance('location', point)
        ).order_by('distance_m')

        if properties.exists():
            visit = Visit.objects.create(
                user=user,
                property=properties.first()
            )
            user.route_processor(visit_id=visit.id)
        return {
            'process_result': True,
            'properties': properties.count()
        }
    raise Exception({
        'user_error': f'user with id {user_id} does not exists'
    })



