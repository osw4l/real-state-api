from celery import shared_task
from .models import CompanyUser
from apps.utils.shortcuts import get_object_or_none


@shared_task
def location_processor(user_id, data, time):
    location = {
        'longitude': data.get('longitude'),
        'latitude': data.get('latitude'),
        'time': time
    }

    user = get_object_or_none(CompanyUser, id=user_id)
    if user:
        return user.store_current_location(location=location)
    raise Exception({
        'user_error': f'user with id {user_id} does not exists'
    })

