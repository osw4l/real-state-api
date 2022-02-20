from functools import wraps
from django.db.models import QuerySet
from rest_framework.response import Response


def add_pagination(func):

    @wraps(func)
    def inner(self, *args, **kwargs):
        queryset = func(self, *args, **kwargs)
        assert isinstance(queryset, (list, QuerySet))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_custom_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_custom_serializer(queryset, many=True)
        return Response(serializer.data)
    return inner
