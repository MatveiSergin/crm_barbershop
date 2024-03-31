from datetime import date

from django.shortcuts import render
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Staff, Appointment
from .serializers import Staff_serializer, Appointment_detail_serializer

class StaffApiView(ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = Staff_serializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['barbershop_id']

class AppointmentDetailListView(ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = Appointment_detail_serializer
    filter_backends = [filters.OrderingFilter]
    #ordering_fields = ['start_time']
    def list(self, request, *args, **kwargs):
        if 'date' in request.query_params:
            query_date = tuple(map(int, request.query_params.get('date').split("-")))
            queryset = Appointment.objects.filter(data__date=date(
                next(query_date[0]),
                next(query_date[1]),
                next(query_date[2])
            ))
        serializer = Appointment_detail_serializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response({"error": "No appointment"})

