from rest_framework.test import APITestCase
from django.db import connection
from corp.models import Appointment, Client, Service, Barbershop, Staff, Position
from corp.serializers import Appointment_detail_serializer
from datetime import datetime
from datetime import date
from django.urls import reverse

class Test_appointment_api(APITestCase):
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

        appointment_datetime1 = datetime(year=2024, month=3, day=18, hour=16, minute=30)
        appointment_datetime2 = datetime(year=2024, month=3, day=19, hour=10, minute=0)

        Appointment.objects.create(
            staff=staff,
            client=client,
            service=service1,
            data=appointment_datetime1,
        )
        Appointment.objects.create(
            staff=staff,
            client=client,
            service=service2,
            data=appointment_datetime2,
        )
    def test_get_for_first_date(self):

        url = 'http://127.0.0.1:8000/api/v1/appointment/?date=2024-03-19'
        response = self.client.get(url)
        response_date = map(int, response.wsgi_request.GET['date'].split("-"))
        appointments = Appointment.objects.filter(data__date=date(next(response_date), next(response_date), next(response_date)))
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_for_second_date(self):
        url = 'http://127.0.0.1:8000/api/v1/appointment/?date=2024-03-18'
        response = self.client.get(url)
        response_date = map(int, response.wsgi_request.GET['date'].split("-"))
        appointments = Appointment.objects.filter(
            data__date=date(next(response_date), next(response_date), next(response_date)))
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_without_date(self):
        #url = 'http://127.0.0.1:8000/api/v1/appointment/'
        url = reverse('appointments')
        response = self.client.get(url)
        appointments = Appointment.objects.all()
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_post_create_when_no_appointments_this_day(self):
        url = reverse('appointments')
        self.client.post(
            path=url,
            data = None
        )
        pass

