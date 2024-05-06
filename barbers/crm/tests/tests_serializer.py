from datetime import time, datetime
from django.utils import timezone

from django.test import TestCase
from django.db import connection

from crm.models import Appointment, Client, Service, Barbershop, Staff, Position, MasterService
from crm.serializers import Appointment_detail_serializer, StaffSerializer, MasterServiceSerializer


class Test_appointment_detail_serializer(TestCase):

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
        self.client = Client.objects.create(
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

        appointment_date1 = timezone.now() + timezone.timedelta(days=1)
        appointment_time1 = time(hour=16, minute=30)
        appointment_datetime1 = datetime.combine(appointment_date1, appointment_time1)

        appointment_date2 = timezone.now() + timezone.timedelta(days=2)
        appointment_time2 = time(hour=10, minute=0)
        appointment_datetime2 = datetime.combine(appointment_date2, appointment_time2)

        self.appointment1 = Appointment.objects.create(
            staff=self.staff,
            client=self.client,
            service=self.service1,
            data=appointment_datetime1,
        )
        self.appointment2 = Appointment.objects.create(
            staff=self.staff,
            client=self.client,
            service=self.service2,
            data=appointment_datetime2,
        )
    def test_data(self):
        appointments = [self.appointment1, self.appointment2]
        serializer_data = Appointment_detail_serializer(appointments, many=True).data
        data = [
            {
                "id": self.appointment1.pk,
                "service": {
                    "id": self.service1.pk,
                    "name": "Service name",
                    "price": 500
                },
                "staff": {
                    "id": self.staff.pk,
                    "name": "Staff_name",
                    "surname": "Staff_surname"
                },
                "client": {
                    "id": self.client.pk,
                    "name": "ClientName",
                    "surname": "ClientSurname",
                    "phone": "+7 (888) 888-88-88"
                },
                "start_time": "16:30",
                "end_time": "17:00"
            },
            {
                "id": self.appointment2.pk,
                "service": {
                    "id": self.service2.pk,
                    "name": "Service name2",
                    "price": 1000
                },
                "staff": {
                    "id": self.staff.pk,
                    "name": "Staff_name",
                    "surname": "Staff_surname"
                },
                "client": {
                    "id": self.client.pk,
                    "name": "ClientName",
                    "surname": "ClientSurname",
                    "phone": "+7 (888) 888-88-88"
                },
                "start_time": "10:00",
                "end_time": "10:30"
            }
        ]

        self.assertEqual(serializer_data, data)


class Test_staff_serializer(TestCase):

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

        self.position1 = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )

        self.position2 = Position.objects.create(
            position='menedjer'
        )

        self.staff1 = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='employee1@yandex.ru',
            position=self.position1,
            barbershop=self.barbershop,
            phone=9998887766,
        )

        self.staff2 = Staff.objects.create(
            name='Staff_name2',
            surname='Staff_surname2',
            patronymic='Staff_patronymic2',
            mail='employee2@yandex.ru',
            position=self.position2,
            barbershop=self.barbershop,
            phone=9998487599,
        )

        self.service1 = Service.objects.create(
            name='Service_name1',
            price=300,
            description='Service_description1'
        )

        self.service2 = Service.objects.create(
            name='Service_name2',
            price=3000,
            description='Service_description2'
        )

        self.master_service1 = MasterService.objects.create(
            staff=self.staff1,
            service=self.service1
        )

        self.master_service2 = MasterService.objects.create(
            staff=self.staff1,
            service=self.service2
        )

    def test_data(self):
        staffs = [self.staff1, self.staff2]
        serializer_data = StaffSerializer(staffs, many=True).data
        data = [
            {
                "id": self.staff1.pk,
                "barbershop": {
                    "id": self.barbershop.pk,
                    "city": "Москва",
                    "street": "Оршанская"
                },
                "name": "Staff_name",
                "surname": "Staff_surname",
                "patronymic": "Staff_patronymic",
                "position": "barber",
                "phone": "+7 (999) 888-77-66",
                "mail": "employee1@yandex.ru",
                "services": [
                    {
                        "service": {
                            "id": self.service1.pk,
                            "name": "Service_name1",
                            "price": 300,
                        }
                    },
                    {
                        "service": {
                            "id": self.service2.pk,
                            "name": "Service_name2",
                            "price": 3000,
                        }
                    }
                ]
            },
            {
                "id": self.staff2.pk,
                "barbershop": {
                    "id": self.barbershop.pk,
                    "city": "Москва",
                    "street": "Оршанская"
                },
                "name": "Staff_name2",
                "surname": "Staff_surname2",
                "patronymic": "Staff_patronymic2",
                "position": "menedjer",
                "phone": "+7 (999) 848-75-99",
                "mail": "employee2@yandex.ru",
                "services": None
            }
        ]

        self.assertEqual(serializer_data, data)

class TestMasterServiceSerializer(TestCase):

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

        self.position1 = Position.objects.create(
            position='barber',
            has_accept_appointments=True
        )

        self.position2 = Position.objects.create(
            position='menedjer'
        )

        self.staff1 = Staff.objects.create(
            name='Staff_name',
            surname='Staff_surname',
            patronymic='Staff_patronymic',
            mail='employee1@yandex.ru',
            position=self.position1,
            barbershop=self.barbershop,
            phone=9998887766,
        )

        self.staff2 = Staff.objects.create(
            name='Staff_name2',
            surname='Staff_surname2',
            patronymic='Staff_patronymic2',
            mail='employee2@yandex.ru',
            position=self.position2,
            barbershop=self.barbershop,
            phone=9998487599,
        )

        self.service1 = Service.objects.create(
            name='Service_name1',
            price=300,
            description='Service_description1'
        )

        self.service2 = Service.objects.create(
            name='Service_name2',
            price=3000,
            description='Service_description2'
        )

        self.master_service1 = MasterService.objects.create(
            staff=self.staff1,
            service=self.service1
        )

        self.master_service2 = MasterService.objects.create(
            staff=self.staff1,
            service=self.service2
        )

    def test_data(self):
        master_services = [self.master_service1, self.master_service2]
        serializer_data = MasterServiceSerializer(master_services, many=True).data

        result_data = [
            {
                "id": self.master_service1.pk,
                "staff": self.staff1.pk,
                "service": self.service1.pk
            },
            {
                "id": self.master_service2.pk,
                "staff": self.staff1.pk,
                "service": self.service2.pk
            }
        ]
        self.assertEqual(serializer_data, result_data)