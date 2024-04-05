from datetime import date, datetime
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ObjectDoesNotExist
from .models import Staff, Appointment, Service, Client
from .serializers import Staff_serializer, Appointment_detail_serializer, ServiceSerializer
from .templates import phonenumber_to_db
from .validators import AppointmentValidator


class StaffApiView(ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = Staff_serializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['barbershop_id']

class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = Appointment_detail_serializer
    filter_backends = [filters.OrderingFilter]
    error_message = 'Order has not been created.'
    #ordering_fields = ['start_time']
    def list(self, request, *args, **kwargs):
        if 'date' in request.query_params:
            query_date = map(int, request.query_params.get('date').split("-"))
            queryset = Appointment.objects.filter(data__date=date(
                next(query_date),
                next(query_date),
                next(query_date)
            ))
        else:
            queryset = Appointment.objects.all()
        serializer = Appointment_detail_serializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response({"error": "No appointment"})

    def create(self, request, *args, **kwargs):
        self.validator = AppointmentValidator()
        self.data = request.data
        self.validator.validate(self.data)

        if not self.validator.is_valid():
            return Response({"error": f"{self.error_message, self.validator.error}"})

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

        serializer = Appointment_detail_serializer(data=serializer_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': f'{self.error_message}'}, status=status.HTTP_400_BAD_REQUEST)

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def create(self, request, *args, **kwargs):
        self.data = request.data
        same_services = Service.objects.filter(name=self.data.get('name'))

        if same_services:
           return Response({'error': 'Service with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        self.data = request.data
        id_service = kwargs['pk']
        old_services = Service.objects.filter(id=id_service)
        if not old_services:
            return Response({'error': 'The service does not exist'}, status=status.HTTP_404_NOT_FOUND)
        old_service = old_services[0]

        if old_service.name != self.data.get('name', None):
            same_services = Service.objects.filter(name=self.data.get('name'))
            if same_services:
                return Response({'error': 'Service with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(self, request, *args, **kwargs)
