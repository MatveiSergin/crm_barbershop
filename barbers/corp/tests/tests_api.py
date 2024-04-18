import json

from rest_framework import status
from rest_framework.test import APITestCase
from django.db import connection
from corp.models import Appointment, Client, Service, Barbershop, Staff, Position, MasterService
from corp.serializers import Appointment_detail_serializer, ServiceSerializer, StaffSerializer
from datetime import datetime
from datetime import date
from django.urls import reverse

from corp.templates import phonenumber_to_show


class TestAppointmentAPI(APITestCase):
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
            schema_editor.create_model(MasterService)

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
            position='barber',
            has_accept_appointments=True
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

        MasterService.objects.create(
            staff=staff,
            service=service1
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
        url = 'http://127.0.0.1:8000/api/v1/appointments/?date=2024-03-19'
        response = self.client.get(url)
        response_date = map(int, response.wsgi_request.GET['date'].split("-"))
        appointments = Appointment.objects.filter(data__date=date(next(response_date), next(response_date), next(response_date)))
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_for_second_date(self):
        url = 'http://127.0.0.1:8000/api/v1/appointments/?date=2024-03-18'
        response = self.client.get(url)
        response_date = map(int, response.wsgi_request.GET['date'].split("-"))
        appointments = Appointment.objects.filter(
            data__date=date(next(response_date), next(response_date), next(response_date)))
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_without_date(self):
        #url = 'http://127.0.0.1:8000/api/v1/appointment/'
        url = 'http://127.0.0.1:8000/api/v1/appointments/'
        response = self.client.get(url)
        appointments = Appointment.objects.all()
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_post_create_when_no_appointments_this_day(self):
        url = 'http://127.0.0.1:8000/api/v1/appointments/'
        service = Service.objects.get(id=1)
        staff = Staff.objects.get(id=1)
        client = Client.objects.get(id=1)
        data = {
            "data": "2024-03-18T17:00",
            "service": {
                "name": service.name
            },
            "staff": {
                "name": staff.name,
                "surname": staff.surname
            },
            "client": {
                "name": client.name,
                "surname": client.surname,
                "phone": client.phone
            }
        }
        response = self.client.post(
            path=url,
            data=data,
            format="json"
        )

        result_data = {
                    "id": 3,
                    "service": {
                        "id": 1,
                        "name": service.name,
                        "price": service.price
                    },
                    "staff": {
                        "id": 1,
                        "name": staff.name,
                        "surname": staff.surname
                    },
                    "client": {
                        "id": 1,
                        "name": client.name,
                        "surname": client.surname,
                        "phone": phonenumber_to_show(client.phone)
                    },
                    "start_time": "17:00",
                    "end_time": "17:30"
        }

        self.assertEqual(response.data, result_data)

    def test_post_when_time_is_busy(self):
        url = 'http://127.0.0.1:8000/api/v1/appointments/'
        service = Service.objects.get(id=1)
        staff = Staff.objects.get(id=1)
        client = Client.objects.get(id=1)
        data = {
            "data": "2024-03-18T16:40",
            "service": {
                "name": service.name
            },
            "staff": {
                "name": staff.name,
                "surname": staff.surname
            },
            "client": {
                "name": client.name,
                "surname": client.surname,
                "phone": client.phone
            }
        }

        response = self.client.post(
            path=url,
            data=data,
            format="json"
        )

        result_data = {
            "error": "('Order has not been created.', 'The master is busy at this time')"
        }

        self.assertEqual(response.data, result_data)

class TestServiceAPI(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Service)
            schema_editor.create_model(MasterService)
            schema_editor.create_model(Staff)
            schema_editor.create_model(Barbershop)
            schema_editor.create_model(Position)

        Service.objects.create(
            price=500,
            name='Service name',
            description='Service description',
        )
        Service.objects.create(
            price=1000,
            name='Service name2',
            description='Service description2',
        )

    def test_get(self):
        url = 'http://127.0.0.1:8000/api/v1/services/'
        response = self.client.get(url)
        services = Service.objects.all()
        result_data = ServiceSerializer(services, many=True).data

        self.assertEqual(response.data, result_data)

    def test_post_when_service_already_exists(self):
        url = 'http://127.0.0.1:8000/api/v1/services/'
        same_service = Service.objects.get(id=1)
        data = ServiceSerializer(same_service).data
        response = self.client.post(url, data)

        result_data = {'error': 'Service with this name already exists'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, result_data)


    def test_post_add_new_service(self):
        url = 'http://127.0.0.1:8000/api/v1/services/'
        new_service = {
            'name': 'Service_3',
            'price': 100,
            'description': 'Lol!'
        }

        self.assertEqual(Service.objects.all().count(), 2)
        json_data = json.dumps(new_service)
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.all().count(), 3)

    def test_put_when_service_already_exists(self):
        id_service = 1
        service = Service.objects.get(id=id_service)
        url = f'http://127.0.0.1:8000/api/v1/services/{id_service}/'
        service_data = ServiceSerializer(service).data
        service_data['price'] = 1000
        response = self.client.put(path=url, data=service_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, service_data)

    def test_put_when_service_does_not_exist(self):
        id_service = 3
        url = f'http://127.0.0.1:8000/api/v1/services/{id_service}/'
        service_data = {
            'name': 'Service name',
            'price': 1000,
            'description': 'Service description'
        }

        response = self.client.put(path=url, data=service_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_when_new_service_name_already_exists(self):
        id_service = 1
        service = Service.objects.get(id=id_service)
        url = f'http://127.0.0.1:8000/api/v1/services/{id_service}/'
        service_data = ServiceSerializer(service).data
        service_data['name'] = 'Service name2'

        response = self.client.put(path=url, data=service_data, format='json')
        result_data = {'error': 'Service with this name already exists'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, result_data)

    def test_delete(self):
        id_service = 1
        url = f'http://127.0.0.1:8000/api/v1/services/{id_service}/'

        response = self.client.delete(path=url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_when_service_does_not_exist(self):
        id_service = 3
        url = f'http://127.0.0.1:8000/api/v1/services/{id_service}/'

        response = self.client.delete(path=url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestStaffAPI(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Service)
            schema_editor.create_model(MasterService)
            schema_editor.create_model(Staff)
            schema_editor.create_model(Barbershop)
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
            position='barber',
            has_accept_appointments=True
        )

        Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=position,
            barbershop=barbershop,
            phone=9998887766,
        )

        staff2 = Staff.objects.create(
            name='Staff_name2',
            surname='Staff_surname2',
            patronymic='Staff_patronymic2',
            mail='qwerty123@yandex.ru',
            position=position,
            barbershop=barbershop,
            phone=9878237462,
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

        MasterService.objects.create(
            staff=staff2,
            service=service1
        )

        MasterService.objects.create(
            staff=staff2,
            service=service2
        )

    def test_get(self):
        url = "http://127.0.0.1:8000/api/v1/staff/"
        staffs = [Staff.objects.get(id=1), Staff.objects.get(id=2)]
        serializer_data = StaffSerializer(staffs, many=True).data
        response = self.client.get(url)
        self.assertEqual(response.data, serializer_data)

    def test_post(self):
        url = f"http://127.0.0.1:8000/api/v1/staff/"

        data = {
            "barbershop": {
                "id": 1
            },
            "name": "Никита",
            "surname": "Пупкин",
            "patronymic": "Антонович",
            "position": "barber",
            "phone": 9988887766,
            "mail": "nikitos04@ya.ru"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, json_data, content_type='application/json')

        result_data = {
            "id": 3,
            "barbershop": {
                "id": 1,
                "city": "Москва",
                "street": "Оршанская"
            },
            "name": "Никита",
            "surname": "Пупкин",
            "patronymic": "Антонович",
            "position": "barber",
            "phone": "+7 (998) 888-77-66",
            "mail": "nikitos04@ya.ru",
            "services": []
        }

        self.assertDictEqual(response.data, result_data)

    def test_patch(self):
        master_id = 1
        url = f"http://127.0.0.1:8000/api/v1/staff/{master_id}/"

        data = {
            "surname": "new_Staff_surname"
        }

        json_data = json.dumps(data)

        response = self.client.patch(url, json_data, content_type='application/json')

        updating_staff = Staff.objects.get(id=master_id)
        result_data = StaffSerializer(updating_staff).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, result_data)
