import json

from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status
from corp.models import Barbershop, Position, Staff
from users.serializers import RegisterSerializer


class TestsRegisterAPI(APITestCase):
    def setUp(self):
        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121545,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber'
        )
        self.group = Group.objects.create(name='Manager')

    def tests_register(self):
        url = "http://127.0.0.1:8000/api/v1/users/register"
        test_request = {
            "barbershop": {
                "id": self.barbershop.id
            },
            "name": "Никита",
            "surname": "Пупкин",
            "patronymic": "Антонович",
            "position": "barber",
            "phone": 9998887768,
            "mail": "nikitos06@ya.ru",
            "password": "rrr"
        }
        json_data = json.dumps(test_request)
        response = self.client.post(url, json_data, content_type="application/json")

        result_data = {
            "login": "nikitos06@ya.ru",
            "password": "rrr"
        }
        self.assertEqual(response.data, result_data)

    def test_register_when_user_exists(self):
        url = "http://127.0.0.1:8000/api/v1/users/register"

        Staff.objects.create(
            name='Никита',
            surname='Пупкин',
            patronymic='Антонович',
            mail='nikitos06@ya.ru',
            position=self.position,
            barbershop=self.barbershop,
            phone=9998887768,
        )

        test_request = {
            "barbershop": {
                "id": self.barbershop.id
            },
            "name": "Никита",
            "surname": "Пупкин",
            "patronymic": "Антонович",
            "position": "barber",
            "phone": 9998887768,
            "mail": "nikitos06@ya.ru",
            "password": "rrr"
        }

        json_data = json.dumps(test_request)
        response = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestLoginAPI(APITestCase):
    def setUp(self):
        self.barbershop = Barbershop.objects.create(
            region='Московская область',
            city='Москва',
            street='Оршанская',
            house='4',
            postal_code=121545,
            mail='orsknka228@mai.com',
            phone=9612345678,
        )

        self.position = Position.objects.create(
            position='barber'
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

        self.password = "password"

        user_serializer = RegisterSerializer(data={
            'name': self.staff.name,
            'surname': self.staff.surname,
            'email': self.staff.mail,
            'password': self.password,
            'staff_id': self.staff.pk
        })
        user_serializer.is_valid(raise_exception=True)
        self.user = user_serializer.save()
        self.group = Group.objects.create(name='Manager')
        self.group.user_set.add(self.user)
    def test_login(self):
        url = "http://127.0.0.1:8000/api/v1/users/login"
        data = {
            "email": self.staff.mail,
            "password": self.password
        }
        json_data = json.dumps(data)
        response = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("jwt" in response.data)

