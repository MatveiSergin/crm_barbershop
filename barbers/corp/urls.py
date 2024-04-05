from rest_framework import routers
from django.urls import path, include
from .views import *

router = routers.SimpleRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'services', ServiceViewSet, basename='services') #http://127.0.0.1:8000/api/v1/service


urlpatterns = [
    path('stafflist/', StaffApiView.as_view(), name='stufflist'), #http://127.0.0.1:8000/api/v1/stafflist/
    path('', include(router.urls)) #http://127.0.0.1:8000/api/v1/appointments?date=2024-03-18
]