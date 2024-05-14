from datetime import date, datetime, time
import datetime

import jwt
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from django.core.exceptions import ObjectDoesNotExist

from barbers.permissions import IsManager, IsManagerOrReadOnly, IsManagerOrIsOwner
from .config import START_WORKING, END_WORKING
from .models import Staff, Appointment, Service, Client, MasterService, Position, Barbershop
from .serializers import StaffSerializer, AppointmentDetailSerializer, ServiceSerializer, FreeTimeSerializer, \
    MasterServiceSerializer
from .templates import phonenumber_to_db, get_free_time, serialize_time_set
from .validators import AppointmentValidator


class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentDetailSerializer
    filter_backends = [filters.OrderingFilter]
    error_message = 'Order has not been created.'
    permission_classes = (IsManagerOrReadOnly, )
    #ordering_fields = ['start_time']
    def list(self, request, *args, **kwargs):
        if 'date' in request.query_params:
            query_date = map(int, request.query_params.get('date').split("-"))
            queryset = Appointment.objects.filter(data__date=date(*query_date))
        else:
            queryset = Appointment.objects.all()
        serializer = AppointmentDetailSerializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response({"detail": "No appointment"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        self.validator = AppointmentValidator()
        self.data = request.data
        self.validator.validate(self.data)

        if not self.validator.is_valid():
            return Response({"detail": f"{self.error_message, self.validator.error}"}, status=status.HTTP_400_BAD_REQUEST)

        valid_data = self.validator.get_validating_data()
        serializer_data = {
            'data': valid_data.get('date'),
            'service': {
                'name': valid_data.get('service').name
            },
            'staff': {
                'name': valid_data.get('staff').name,
                'surname': valid_data.get('staff').surname
            },
            'client': {
                'name': valid_data.get('client').name,
                'surname': valid_data.get('client').surname,
                'phone': valid_data.get('client').phone
            }
        }

        serializer = AppointmentDetailSerializer(data=serializer_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': f'{self.error_message}'}, status=status.HTTP_400_BAD_REQUEST)

class ServiceViewSet(LoginRequiredMixin, ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (IsManagerOrReadOnly,)
    def create(self, request, *args, **kwargs):
        self.data = request.data
        same_services = Service.objects.filter(name=self.data.get('name'))

        if same_services:
           return Response({'detail': 'Service with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        self.data = request.data
        id_service = kwargs['pk']
        old_services = Service.objects.filter(id=id_service)
        if not old_services:
            return Response({'detail': 'The service does not exist'}, status=status.HTTP_404_NOT_FOUND)
        old_service = old_services[0]

        if old_service.name != self.data.get('name', None):
            same_services = Service.objects.filter(name=self.data.get('name'))
            if same_services:
                return Response({'detail': 'Service with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(self, request, *args, **kwargs)

class StaffVeiwSet(LoginRequiredMixin, ModelViewSet):
    queryset = Staff.objects.all()
    permission_classes = (IsManagerOrIsOwner, )
    serializer_class = StaffSerializer
    filterset_fields = ['barbershop__city',
                        'barbershop__street',
                        'barbershop__postal_code',
                        'barbershop__id',
                        'name',
                        'surname']

class FreeTimes(APIView):
    permission_classes = (IsManager, )
    def get(self, request):
        if not 'master_id' in request.query_params and 'date' in request.query_params:
            return Response({'detail': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        master_id = request.query_params.get('master_id')

        if not Staff.objects.filter(id=master_id):
            return Response({"detail": "Master not found"}, status=status.HTTP_400_BAD_REQUEST)

        query_date = map(int, request.query_params.get('date').split("-"))
        queryset = Appointment.objects.filter(data__date=date(
            next(query_date),
            next(query_date),
            next(query_date)
        )).filter(
            staff=master_id
        )
        free_times = get_free_time(queryset)
        times_for_serializer = serialize_time_set(free_times)
        if times_for_serializer:
            return Response({'times': sorted(times_for_serializer['times'])})
        else:
            return Response({"detail": "Master not found"}, status=status.HTTP_400_BAD_REQUEST)

class MasterServiceAPI(LoginRequiredMixin, ModelViewSet):
    queryset = MasterService.objects.all()
    serializer_class = MasterServiceSerializer