from datetime import datetime, time
from django.db import connection
from django.test import TestCase
from corp.models import Appointment, Staff, Client, Service, Barbershop, Position
from django.utils import timezone
from django.core.validators import validate_email
from unittest.mock import Mock



class AppointmentTest(TestCase):
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
            service = Service.objects.create(
                price=500,
                name='Service name',
                description='Service description',
            )

            appointment_date = timezone.now() + timezone.timedelta(days=1)  # Назначаем на завтра
            appointment_time = time(hour=16, minute=30)
            appointment_datetime = datetime.combine(appointment_date, appointment_time)

            appointment = Appointment.objects.create(
                staff=staff,
                client=client,
                service=service,
                data=appointment_datetime,
            )

    def test_staff_position(self):
        appointment = Appointment.objects.get(id=1)
        position = appointment.staff.position.position
        self.assertNotEqual(position, 'менеджер')

    def test_object_name_is_full_name_staff_and_data(self):
        appointment = Appointment.objects.get(id=1)
        staff_full_name, data = str(appointment).split("|")
        self.assertEqual(staff_full_name, 'Staff_name Staff_surname')
        self.assertEqual(data, datetime.combine(timezone.now() + timezone.timedelta(days=1), time(16, 30)).strftime("%d/%m/%Y %H:%M"))

    def test_data_not_in_past(self):
        appointment = Appointment.objects.get(id=1)
        self.assertTrue(appointment.data > timezone.now())

    def test_status_code(self):
        appointment = Appointment.objects.get(id=1)
        self.assertEqual(appointment.status_code, 0)
        appointment.status_code = 1
        self.assertEqual(appointment.status_code, 1)

class ClientTest(TestCase):
    def setUp(self):
        super().setUpTestData()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Client)

        client = Client.objects.create(
             name='Clientname',
             surname='Clientsurname',
             mail='matvei.sergin2016@yandex.ru',
             phone=8888888888,
        )


    def test_email(self):
        client = Client.objects.get(id=1)
        self.assertEqual(client.mail, "matvei.sergin2016@yandex.ru")
        client.mail = "matveiEmail"
        client.save()
        self.assertEqual(client.mail, None)