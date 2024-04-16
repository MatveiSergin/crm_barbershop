from django.db import models
import datetime

from django.core.exceptions import ValidationError

from corp.templates import phonenumber_to_db
from django.core.validators import validate_email, EmailValidator

class Appointment(models.Model):
    staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=True)
    client = models.ForeignKey('Client', models.DO_NOTHING, blank=True)
    service = models.ForeignKey('Service', models.DO_NOTHING, blank=True)
    status_code = models.IntegerField(blank=True, default=0)
    data = models.DateTimeField(blank=True)

    class Meta:
        managed = False
        db_table = 'appointment'

    def __str__(self):
        return f'{self.staff.get_full_name()}|{self.data.strftime("%d/%m/%Y %H:%M")}'


class Barbershop(models.Model):
    region = models.CharField(blank=True, null=True)
    city = models.CharField(blank=True, null=True)
    street = models.CharField(blank=True, null=True)
    house = models.CharField(blank=True, null=True)
    postal_code = models.IntegerField(unique=True, blank=True, null=True)
    phone = models.BigIntegerField(unique=True, blank=True, null=True)
    mail = models.CharField(unique=True)

    def save(self, *args, **kwargs):
        self.phone = phonenumber_to_db(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.city}-{self.street}'
    class Meta:
        managed = False
        db_table = 'barbershop'


class Client(models.Model):
    name = models.CharField()
    surname = models.CharField()
    phone = models.BigIntegerField()
    mail = models.CharField(unique=True, blank=True, null=True, validators=[validate_email])

    def save(self, *args, **kwargs):
        self.phone = phonenumber_to_db(self.phone)
        try:
            ev = EmailValidator()
            if self.mail is not None:
                ev(self.mail)
        except ValidationError:
            #print(f"Invalid email for client {self.name} {self.surname}")
            self.mail = None
        finally:
            super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'client'


class Documents(models.Model):
    staff = models.OneToOneField('Staff', models.DO_NOTHING, primary_key=True)
    passport = models.BigIntegerField(unique=True)
    employment_record_number = models.BigIntegerField(unique=True)
    snils = models.BigIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'documents'


class MasterService(models.Model):
    staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=True, null=True)
    service = models.ForeignKey('Service', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_service'


class Position(models.Model):
    position = models.CharField(unique=True)
    has_accept_appointments = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'position'


class Service(models.Model):
    price = models.IntegerField()
    name = models.CharField()
    description = models.CharField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if (self.price < 0):
            self.price = None
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'service'


class Staff(models.Model):
    barbershop = models.ForeignKey(Barbershop, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField()
    surname = models.CharField()
    patronymic = models.CharField(blank=True, null=True)
    position = models.ForeignKey(Position, models.DO_NOTHING)
    phone = models.BigIntegerField(unique=True)
    mail = models.CharField(unique=True)

    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        self.phone = phonenumber_to_db(self.phone)
        try:
            ev = EmailValidator()
            if self.mail is not None:
                ev(self.mail)
        except ValidationError:
            self.mail = None
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'staff'