from datetime import datetime

from django.shortcuts import _get_queryset


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except:
        return None


def filter_kwargs_builder(uuid, date):
    date = datetime.strptime(date, '%Y-%m-%d')
    return {
        'user__uuid': uuid,
        'created_at__day': date.day,
        'created_at__month': date.month,
        'created_at__year': date.year
    }
