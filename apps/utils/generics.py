from rest_framework import viewsets


class RealStateGenericViewSet(viewsets.GenericViewSet):
    custom_serializer_class = None

    def get_custom_serializer(self, *args, **kwargs):
        custom_serializer_class = self.get_custom_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return custom_serializer_class(*args, **kwargs)

    def get_custom_serializer_class(self):
        assert self.custom_serializer_class is not None, (
                "'%s' should either include a `custom_serializer` attribute, "
                "or override the `get_custom_serializer_class()` method."
                % self.__class__.__name__
        )
        return self.custom_serializer_class
