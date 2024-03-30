from datetime import date

from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Staff, Appointment
from .serializers import Staff_serializer, Appointment_detail_serializer

class StaffApiView(ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = Staff_serializer


class AppointmentDetailListView(ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = Appointment_detail_serializer

    def list(self, request, *args, **kwargs):
        query_date = map(int, request.query_params.get('date').split("-"))
        queryset = Appointment.objects.filter(data__date=date(next(query_date), next(query_date), next(query_date)))
        serializer = Appointment_detail_serializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response({"error": "No appointment"})

