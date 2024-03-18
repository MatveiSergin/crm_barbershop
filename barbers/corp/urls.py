from django.urls import path
from .views import *


urlpatterns = [
    path('stafflist/', StaffApiView.as_view(), name='stufflist'), #http://127.0.0.1:8000/api/v1/stafflist/
    path('stafftest/', StaffAPIViewTest.as_view(), name='test'),
    ]