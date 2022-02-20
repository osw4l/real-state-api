from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'users', viewsets.CompanyUserAuthViewSet)

urlpatterns = [
    path('', include(router.urls))
]
