from datetime import datetime, time

from django.db import connection
from django.test import TestCase
from crm.models import Appointment, Staff, Client, Service, Barbershop, Position
from django.utils import timezone

class AppointmentTest(TestCase):
    def setUp(self):
        self.barbershop = Barbershop.objects.create(
                region='Московская область',
                city='Москва',
                street='Оршанский',
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
        self.client = Client.objects.create(
                name='ClientName',
                surname='ClientSurname',
                mail='matvei.sergin2016@yandex.ru',
                phone=8888888888,
            )
        self.service = Service.objects.create(
                price=500,
                name='Service name',
                description='Service description',
            )

        appointment_date = timezone.now() + timezone.timedelta(days=1)  # Назначаем на завтра
        appointment_time = time(hour=16, minute=30)
        appointment_datetime = datetime.combine(appointment_date, appointment_time)

        self.appointment = Appointment.objects.create(
                staff=self.staff,
                client=self.client,
                service=self.service,
                data=appointment_datetime,
            )

    def test_staff_position(self):
        position = self.appointment.staff.position.position
        self.assertEqual(position, 'barber')

    def test_object_name_is_full_name_staff_and_data(self):
        staff_full_name, data = str(self.appointment).split("|")
        self.assertEqual(staff_full_name, 'Staff_name Staff_surname')
        self.assertEqual(data, datetime.combine(timezone.now() + timezone.timedelta(days=1), time(16, 30)).strftime("%d/%m/%Y %H:%M"))

    def test_data_not_in_past(self):
        self.assertTrue(self.appointment.data > timezone.now())

    def test_status_code(self):
        self.assertEqual(self.appointment.status_code, 0)
        self.appointment.status_code = 1
        self.assertEqual(self.appointment.status_code, 1)

class ClientTest(TestCase):
    def setUp(self):

        self.client = Client.objects.create(
             name='Clientname',
             surname='Clientsurname',
             mail='matvei.sergin2016@yandex.ru',
             phone=8888888888,
        )


    def test_email(self):
        self.assertEqual(self.client.mail, "matvei.sergin2016@yandex.ru")
        self.client.mail = "matveiEmail"
        self.client.save()
        self.assertEqual(self.client.mail, None)