from datetime import datetime, date

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

from crm.config import DURATION_OF_SERVICE, START_WORKING, END_WORKING
from crm.models import Service, Staff, Client, MasterService, Appointment
from crm.templates import phonenumber_to_db


class AppointmentValidator:
    def __init__(self):
        self.error = None
        self.result = None

    def is_valid(self, initial_data=None):
        if self.result is not None:
            return self.result
        elif initial_data is not None:
            self.validate(initial_data)
            return self.result
        elif self.result is None and initial_data is None:
            return None

    def validate(self, initial_data):
        self._parse_data(initial_data)
        self._init_fields()
        self._run_validator()
    def get_validating_data(self):
        if self.result:
            return {'staff': self.staff,
                    'client': self.client,
                    'service': self.service,
                    'date': self.date}

    def _parse_data(self, data):
        self.staff_data = data.get('staff', None)
        self.client_data = data.get('client', None)
        self.service_data = data.get('service', None)
        self.date_data = data.get('data', None)

    def _init_fields(self):
        self.staff = None
        self.client = None
        self.service = None
        self.date = None

    def _run_validator(self):
        for validator in (self._validating_staff, self._validating_client, self._validating_service, self._validating_date):
            validator()

            if self.error:
                self.result = False
                break

        else:
            self.result = True


    def _validating_staff(self):
        if not self.staff_data:
            self.error = "No master name provided"
            return

        staff_name, staff_surname = self.staff_data.get('name', None), self.staff_data.get('surname', None)
        if staff_name and staff_surname:
            staffs = Staff.objects.filter(name=staff_name).filter(surname=staff_surname)
        if staffs:
            possible_staff = staffs.first()
            if possible_staff.position.has_accept_appointments:
                self.staff = possible_staff
            else:
                self.error = "Staff has not accept appointments"
                return
        else:
            self.error = "Staff not found"
            return

    def _validating_client(self):
        if not self.client_data:
            self.error = "No client name provided"
            return
        try:
            client_phone = phonenumber_to_db( self.client_data.get('phone', None))
        except ValueError as ex:
            self.error = str(ex)
            return

        try:
            self.client = Client.objects.get(phone=client_phone)
            if self.client.name != self.client_data.get('name') or self.client.surname !=  self.client_data.get('surname'):
                self.error = "Name and surname do not match the data under this number."
                return
        except ObjectDoesNotExist:
            client_name =  self.client_data.get('name', None)
            client_surname =  self.client_data.get('surname', None)
            if client_name and client_surname:
                self.client = Client.objects.create(
                    name=client_name,
                    surname=client_surname,
                    phone=client_phone,
                )
            else:
                self.error = "Clients name and surname must be not empty"
                return

    def _validating_service(self):
        if not self.service_data:
            self.error = "No service name provided"
            return
        service_name = self.service_data.get('name', None)
        if service_name:
            services = Service.objects.filter(name=service_name)
            if services:
                self.service = services[0]
                if not MasterService.objects.filter(staff=self.staff).filter(service=self.service):
                    self.error = "The master does not provide this service"
                    return
            else:
                self.error = "Service not found"
                return
        else:
            self.error = "No service name provided"
            return


    def _validating_date(self):
        self.date = self.date_data
        services_time = datetime.strptime(self.date, '%Y-%m-%dT%H:%M')

        appointments = Appointment.objects.filter(data__date=date(
            services_time.year,
            services_time.month,
            services_time.day
        )).order_by('data')
        for appointment in appointments:
            if not START_WORKING <= services_time.time() <= END_WORKING:
                self.error = "The barbershop is not working at this time"
            elif appointment.data < services_time and appointment.data + DURATION_OF_SERVICE > services_time:
                self.error = "The master is busy at this time"
                return
            elif appointment.data > services_time and appointment.data - DURATION_OF_SERVICE < services_time:
                self.error = "The master is busy at this time"
                return
        if not self.date:
            self.error = "Date is empty"
            return

