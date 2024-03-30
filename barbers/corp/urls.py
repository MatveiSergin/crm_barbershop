from django.urls import path
from .views import *


urlpatterns = [
    path('stafflist/', StaffApiView.as_view(), name='stufflist'), #http://127.0.0.1:8000/api/v1/stafflist/
    path('appointment/', AppointmentDetailListView.as_view(), name='appointment') #http://127.0.0.1:8000/api/v1/appointment?date=123
    ]