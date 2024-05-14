import json

import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import connection
from crm.models import Appointment, Client, Service, Barbershop, Staff, Position, MasterService
from crm.serializers import AppointmentDetailSerializer, ServiceSerializer, StaffSerializer, MasterServiceSerializer
from datetime import datetime, timedelta
from datetime import date
from django.urls import reverse

from crm.templates import phonenumber_to_show


class TestAppointmentAPI(APITestCase):

    def setUp(self):

        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121552,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )
        self.staff = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9998887766,
        )
        self.customers = Client.objects.create(
            name='ClientName',
            surname='ClientSurname',
            mail='matvei.sergin2016@yandex.ru',
            phone=8888888888,
        )
        self.service1 = Service.objects.create(
            price=500,
            name='Service name',
            description='Service description',
        )
        self.service2 = Service.objects.create(
            price=1000,
            name='Service name2',
            description='Service description2',
        )

        MasterService.objects.create(
            staff=self.staff,
            service=self.service1
        )

        appointment_datetime1 = datetime(year=2024, month=3, day=18, hour=16, minute=30)
        appointment_datetime2 = datetime(year=2024, month=3, day=19, hour=10, minute=0)

        Appointment.objects.create(
            staff=self.staff,
            client=self.customers,
            service=self.service1,
            data=appointment_datetime1,
        )
        Appointment.objects.create(
            staff=self.staff,
            client=self.customers,
            service=self.service2,
            data=appointment_datetime2,
        )

        self.user = get_user_model().objects.create_user(
            username=self.staff.mail,
            email=self.staff.mail,
            password="password",
            first_name=self.staff.name,
            last_name=self.staff.surname,
            staff=self.staff,

        )

        self.group = Group.objects.create(name='Manager')
        self.group.user_set.add(self.user)

    def test_get_for_first_date(self):
        appointments_url = reverse('appointments-list')
        date_param = '2024-03-19'
        url = f'{appointments_url}?date={date_param}'
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        response_date = map(int, response.wsgi_request.GET['date'].split("-"))
        appointments = Appointment.objects.filter(data__date=date(next(response_date), next(response_date), next(response_date)))
        serializer_data = AppointmentDetailSerializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_for_second_date(self):
        appointments_url = reverse('appointments-list')
        date_param = '2024-03-19'
        url = f'{appointments_url}?date={date_param}'
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        response_date = map(int, response.wsgi_request.GET['date'].split("-"))
        appointments = Appointment.objects.filter(data__date=date(*response_date))
        serializer_data = AppointmentDetailSerializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_without_date(self):
        url = reverse('appointments-list')
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        appointments = Appointment.objects.all()
        serializer_data = AppointmentDetailSerializer(appointments, many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_post_create_when_no_appointments_this_day(self):
        url = reverse('appointments-list')
        data = {
            "data": "2024-03-18T17:00",
            "service": {
                "name": self.service1.name
            },
            "staff": {
                "name": self.staff.name,
                "surname": self.staff.surname
            },
            "client": {
                "name": self.customers.name,
                "surname": self.customers.surname,
                "phone": self.customers.phone
            }
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(
            path=url,
            data=data,
            format="json"
        )

        result_data = {
                    "id": Appointment.objects.all().last().pk,
                    "service": {
                        "id": self.service1.pk,
                        "name": self.service1.name,
                        "price": self.service1.price
                    },
                    "staff": {
                        "id": self.staff.pk,
                        "name": self.staff.name,
                        "surname": self.staff.surname
                    },
                    "client": {
                        "id": self.customers.pk,
                        "name": self.customers.name,
                        "surname": self.customers.surname,
                        "phone": phonenumber_to_show(self.customers.phone)
                    },
                    "start_time": "17:00",
                    "end_time": "17:30"
        }

        self.assertEqual(response.data, result_data)

    def test_post_when_time_is_busy(self):
        url = reverse('appointments-list')
        data = {
            "data": "2024-03-18T16:40",
            "service": {
                "name": self.service1.name
            },
            "staff": {
                "name": self.staff.name,
                "surname": self.staff.surname
            },
            "client": {
                "name": self.customers.name,
                "surname": self.customers.surname,
                "phone": self.customers.phone
            }
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(
            path=url,
            data=data,
            format="json"
        )

        result_data = {
            "detail": "('Order has not been created.', 'The master is busy at this time')"
        }

        self.assertEqual(response.data, result_data)

class TestServiceAPI(APITestCase):

    def setUp(self):
        self.service1 = Service.objects.create(
            price=500,
            name='Service name',
            description='Service description',
        )
        self.service2 = Service.objects.create(
            price=1000,
            name='Service name2',
            description='Service description2',
        )

        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121552,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )
        self.staff = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9998887766,
        )

        self.user = get_user_model().objects.create_user(
            username=self.staff.mail,
            email=self.staff.mail,
            password="password",
            first_name=self.staff.name,
            last_name=self.staff.surname,
            staff=self.staff
        )

        self.group = Group.objects.create(name='Manager')
        self.group.user_set.add(self.user)

        payload = {
            "id": self.user.id,
            "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
            "iet": datetime.now().timestamp()
        }

        self.token = jwt.encode(payload=payload, key='secret', algorithm='HS256')

    def test_get(self):
        url = reverse('services-list')
        self.client.cookies['jwt'] = self.token
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        services = Service.objects.all()
        result_data = ServiceSerializer(services, many=True).data
        self.assertEqual(response.data, result_data)

    def test_post_when_service_already_exists(self):
        url = reverse('services-list')
        same_service = self.service1
        data = ServiceSerializer(same_service).data
        self.client.cookies['jwt'] = self.token
        self.client.force_login(user=self.user)
        response = self.client.post(url, data)

        result_data = {'detail': 'Service with this name already exists'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, result_data)


    def test_post_add_new_service(self):
        url = reverse('services-list')
        new_service = {
            'name': 'Service_3',
            'price': 100,
            'description': 'Lol!'
        }

        self.assertEqual(Service.objects.all().count(), 2)
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        json_data = json.dumps(new_service)
        response = self.client.post(url, json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.all().count(), 3)

    def test_put_when_service_already_exists(self):
        url = reverse('services-detail', kwargs={'pk': self.service1.pk})
        service_data = ServiceSerializer(self.service1).data
        service_data['price'] = 1000
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.put(path=url, data=service_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, service_data)

    def test_put_when_service_does_not_exist(self):
        service_id_not_exists = self.service2.pk + 1
        url = reverse('services-detail', kwargs={'pk': service_id_not_exists})
        service_data = {
            'name': 'Service name',
            'price': 1000,
            'description': 'Service description'
        }
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.put(path=url, data=service_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_when_new_service_name_already_exists(self):
        url = reverse('services-detail', kwargs={'pk': self.service1.pk})

        service_data = ServiceSerializer(self.service1).data
        service_data['name'] = 'Service name2'

        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.put(path=url, data=service_data, format='json')
        result_data = {'detail': 'Service with this name already exists'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, result_data)

    def test_delete(self):
        url = reverse('services-detail', kwargs={'pk': self.service1.pk})
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.delete(path=url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_when_service_does_not_exist(self):
        service_id_not_exists = self.service2.pk + 1
        url = reverse('services-detail', kwargs={'pk': service_id_not_exists})
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.delete(path=url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestStaffAPI(APITestCase):

    def setUp(self):

        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121552,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )

        self.staff1 = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9998887766,
        )

        self.staff2 = Staff.objects.create(
            name='Staff_name2',
            surname='Staff_surname2',
            patronymic='Staff_patronymic2',
            mail='qwerty123@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9878237462,
        )

        self.service1 = Service.objects.create(
            price=500,
            name='Service name',
            description='Service description',
        )
        self.service2 = Service.objects.create(
            price=1000,
            name='Service name2',
            description='Service description2',
        )

        self.master_service1 = MasterService.objects.create(
            staff=self.staff2,
            service=self.service1
        )

        self.master_service2 = MasterService.objects.create(
            staff=self.staff2,
            service=self.service2
        )

        self.user = get_user_model().objects.create_user(
            username=self.staff1.mail,
            email=self.staff1.mail,
            password="password",
            first_name=self.staff1.name,
            last_name=self.staff1.surname,
            staff=self.staff1
        )

        self.group = Group.objects.create(name='Manager')
        self.group.user_set.add(self.user)

        payload = {
            "id": self.user.id,
            "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
            "iet": datetime.now().timestamp()
        }

        self.token = jwt.encode(payload=payload, key='secret', algorithm='HS256')

    def test_get(self):
        url = reverse('staff-list')
        staffs = [self.staff1, self.staff2]
        serializer_data = StaffSerializer(staffs, many=True).data
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.data, serializer_data)

    def test_post(self):
        url = reverse('staff-list')

        data = {
            "barbershop": {
                "id": Barbershop.objects.all().last().pk
            },
            "name": "Никита",
            "surname": "Пупкин",
            "patronymic": "Антонович",
            "position": "barber",
            "phone": 9988887766,
            "mail": "nikitos04@ya.ru"
        }
        json_data = json.dumps(data)

        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.post(url, json_data, content_type='application/json')

        result_data = {
            "id": Staff.objects.all().last().pk,
            "barbershop": {
                "id": Barbershop.objects.all().last().pk,
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
        url = reverse('staff-detail', kwargs={'pk': self.staff1.pk})
        data = {
            "surname": "new_Staff_surname"
        }

        json_data = json.dumps(data)
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.patch(url, json_data, content_type='application/json')

        updating_staff = Staff.objects.get(id=self.staff1.pk)
        result_data = StaffSerializer(updating_staff).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, result_data)

class TestMasterServiceAPI(APITestCase):
    def setUp(self):

        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121552,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )

        self.staff1 = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9998887766,
        )

        self.staff2 = Staff.objects.create(
            name='Staff_name2',
            surname='Staff_surname2',
            patronymic='Staff_patronymic2',
            mail='qwerty123@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9878237462,
        )

        self.service1 = Service.objects.create(
            price=500,
            name='Service name',
            description='Service description',
        )
        self.service2 = Service.objects.create(
            price=1000,
            name='Service name2',
            description='Service description2',
        )

        self.master_service1 = MasterService.objects.create(
            staff=self.staff2,
            service=self.service1
        )

        self.master_service2 = MasterService.objects.create(
            staff=self.staff2,
            service=self.service2
        )

        self.user = get_user_model().objects.create_user(
            username=self.staff1.mail,
            email=self.staff1.mail,
            password="password",
            first_name=self.staff1.name,
            last_name=self.staff1.surname,
            staff=self.staff1
        )

        self.group = Group.objects.create(name='Manager')
        self.group.user_set.add(self.user)

        payload = {
            "id": self.user.id,
            "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
            "iet": datetime.now().timestamp()
        }

        self.token = jwt.encode(payload=payload, key='secret', algorithm='HS256')

    def test_get(self):
        url = reverse('master_services-list')
        master_services = [self.master_service1, self.master_service2]
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.get(url)
        result_data = MasterServiceSerializer(master_services, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, result_data)

    def test_post(self):
        url = reverse('master_services-list')

        data = {
            "staff": Staff.objects.all().last().pk - 1,
            "service": Service.objects.all().last().pk - 1
        }
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response = self.client.post(url, data, format='json')

        result_data = {
            "id": MasterService.objects.all().last().pk,
            "staff": Staff.objects.all().last().pk - 1,
            "service": Service.objects.all().last().pk - 1
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, result_data)

    def test_put_and_patch(self):
        url = reverse('master_services-detail', kwargs={'pk': self.master_service1.pk})
        data = {
            "staff": Staff.objects.all().last().pk,
            "service": Service.objects.all().last().pk
        }
        self.client.cookies['jwt'] = self.token
        self.client.force_login(self.user)
        response1 = self.client.put(url, data, format='json')
        response2 = self.client.patch(url, data, format='json')

        self.assertEqual(response1.status_code, response2.status_code)
        self.assertEqual(response1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestFreeTime(APITestCase):
    def setUp(self):
        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121552,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )

        self.staff = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='matvei.sergin2016@yandex.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9998887766,
        )

        self.service = Service.objects.create(
            price=1000,
            name='Service name',
            description='Service description',
        )

        self.customers = Client.objects.create(
            name='ClientName',
            surname='ClientSurname',
            mail='matvei.sergin2016@yandex.ru',
            phone=8888888888,
        )

        self.appointment_datetime = datetime(year=2024, month=3, day=18, hour=16, minute=30)

        self.appointment = Appointment.objects.create(
            staff=self.staff,
            client=self.customers,
            service=self.service,
            data=self.appointment_datetime,
        )

        self.user = get_user_model().objects.create_user(
            username=self.staff.mail,
            email=self.staff.mail,
            password="password",
            first_name=self.staff.name,
            last_name=self.staff.surname,
            staff=self.staff
        )

        self.group = Group.objects.create(name='Manager')
        self.group.user_set.add(self.user)

        payload = {
            "id": self.user.id,
            "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
            "iet": datetime.now().timestamp()
        }

        self.token = jwt.encode(payload=payload, key='secret', algorithm='HS256')

    def test_get_free_times(self):
        free_times_url = reverse('FreeTimes')
        url = f"{free_times_url}?master_id={self.staff.pk}&date={self.appointment_datetime.strftime("%Y-%m-%d")}"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        result_data = {'times': ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30']}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, result_data)
