from celery import shared_task
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from apps.utils.shortcuts import get_object_or_none


@shared_task
def setup_visits(user_id, latitude, longitude):
    from .models import Property, Visit
    from apps.auth2.models import CompanyUser
    user = get_object_or_none(CompanyUser, id=user_id)
    if user:
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

