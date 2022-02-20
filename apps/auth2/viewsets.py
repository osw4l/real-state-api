from datetime import datetime
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.utils.permissions import IsCompanyUser
from apps.main.serializers import VisitSerializer
from apps.utils.pagination import CustomPagination
from apps.main.models import Visit
from apps.utils.serializers import DateFilterSerializer
from . import tasks
from .models import CompanyUser, SpeedReport
from .serializers import (
    CompanyUserSerializer,
    UserLoginSerializer,
    LocationSerializer,
    SpeedReportSerializer
)
from apps.utils.decorators import add_pagination
from apps.utils.generics import RealStateGenericViewSet


class CompanyUserAuthViewSet(RealStateGenericViewSet):
    serializer_class = CompanyUserSerializer
    queryset = CompanyUser.objects.filter(deleted=False)
    permission_classes = [
        IsAuthenticated,
        IsCompanyUser,
    ]
    lookup_field = 'uuid'
    pagination_class = CustomPagination

    @action(detail=False,
            methods=['POST'],
            permission_classes=[AllowAny],
            serializer_class=UserLoginSerializer)
    def login(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        return Response({
            'user': user,
            'token': token
        })

    @action(detail=False,
            methods=['POST'],
            serializer_class=LocationSerializer)
    def location(self, request):
        self.serializer_class(data=request.data).is_valid(raise_exception=True)

        time = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        tasks.location_processor.delay(self.request.user.id, request.data, time)

        return Response({
            "location_sent": True
        })

    @add_pagination
    @action(detail=True,
            methods=['POST'],
            permission_classes=[AllowAny],
            serializer_class=DateFilterSerializer,
            custom_serializer_class=VisitSerializer)
    def visits(self, request, uuid=None):
        date_serializer = self.serializer_class(data=request.data)
        date_serializer.is_valid(raise_exception=True)
        return Visit.filter_by_date_and_user(
            user_uuid=uuid,
            date=date_serializer.data.get('date')
        )

    @add_pagination
    @action(detail=True,
            methods=['POST'],
            permission_classes=[AllowAny],
            serializer_class=DateFilterSerializer,
            custom_serializer_class=SpeedReportSerializer)
    def routes(self, request, uuid=None):
        date_serializer = self.serializer_class(data=request.data)
        date_serializer.is_valid(raise_exception=True)

        return SpeedReport.filter_by_date_and_user(
            user_uuid=uuid,
            date=date_serializer.data.get('date')
        )

