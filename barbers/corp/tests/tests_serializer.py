from datetime import time, datetime
from django.utils import timezone

from django.test import TestCase
from django.db import connection

from corp.models import Appointment, Client, Service, Barbershop, Staff, Position
from corp.serializers import Appointment_detail_serializer


class test_AppointmentDetailSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Appointment)
            schema_editor.create_model(Client)
            schema_editor.create_model(Service)
            schema_editor.create_model(Barbershop)
            schema_editor.create_model(Staff)
            schema_editor.create_model(Position)

        barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121552,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        position = Position.objects.create(
            position='barber'
        )
        staff = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=position,
            barbershop=barbershop,
            phone=9998887766,
        )
        client = Client.objects.create(
            name='ClientName',
            surname='ClientSurname',
            mail='matvei.sergin2016@yandex.ru',
            phone=8888888888,
        )
        service1 = Service.objects.create(
            price=500,
            name='Service name',
            description='Service description',
        )
        service2 = Service.objects.create(
            price=1000,
            name='Service name2',
            description='Service description2',
        )

        appointment_date1 = timezone.now() + timezone.timedelta(days=1)
        appointment_time1 = time(hour=16, minute=30)
        appointment_datetime1 = datetime.combine(appointment_date1, appointment_time1)

        appointment_date2 = timezone.now() + timezone.timedelta(days=2)
        appointment_time2 = time(hour=10, minute=0)
        appointment_datetime2 = datetime.combine(appointment_date2, appointment_time2)

        appointment1 = Appointment.objects.create(
            staff=staff,
            client=client,
            service=service1,
            data=appointment_datetime1,
        )
        appointment2 = Appointment.objects.create(
            staff=staff,
            client=client,
            service=service2,
            data=appointment_datetime2,
        )
    def test_data(self):
        ap1 = Appointment.objects.get(id=1)
        ap2 = Appointment.objects.get(id=2)
        serializer_data = Appointment_detail_serializer([ap1, ap2], many=True).data
        data = [
            {
                "service": {
                    "name": "Service name",
                    "price": 500
                },
                "staff": {
                    "name": "Staff_name",
                    "surname": "Staff_surname"
                },
                "client": {
                    "name": "ClientName",
                    "surname": "ClientSurname",
                    "phone": "+7 (888) 888-88-88"
                },
                "start_time": "16:30",
                "end_time": "17:00"
            },
            {
                "service": {
                    "name": "Service name2",
                    "price": 1000
                },
                "staff": {
                    "name": "Staff_name",
                    "surname": "Staff_surname"
                },
                "client": {
                    "name": "ClientName",
                    "surname": "ClientSurname",
                    "phone": "+7 (888) 888-88-88"
                },
                "start_time": "10:00",
                "end_time": "10:30"
            }
        ]

        self.assertEqual(serializer_data, data)