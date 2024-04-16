from rest_framework import routers
from django.urls import path, include
from .views import *

router = routers.SimpleRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'staff', StaffVeiwSet, basename='staff') #http://127.0.0.1:8000/api/v1/staff/
router.register(r'services', ServiceViewSet, basename='services') #http://127.0.0.1:8000/api/v1/services/


urlpatterns = [
    path('', include(router.urls)), #http://127.0.0.1:8000/api/v1/appointments?date=2024-03-18
    path('FreeTimes', FreeTimes.as_view()) #http://127.0.0.1:8000/api/v1/FreeTimes/
]