from django.db import models


class Appointment(models.Model):
    staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=True, null=True)
    client = models.ForeignKey('Client', models.DO_NOTHING, blank=True, null=True)
    full_name_client = models.CharField(max_length=60)
    phone = models.TextField(blank=True, null=True)
    service = models.ForeignKey('Service', models.DO_NOTHING, blank=True, null=True)
    data = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'appointment'


class Barbershop(models.Model):
    address = models.TextField()
    phone = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'barbershop'


class Client(models.Model):
    full_name = models.CharField(max_length=60)
    phone = models.TextField(unique=True)
    mail = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'client'


class Documents(models.Model):
    id = models.OneToOneField('Staff', models.DO_NOTHING, db_column='id', primary_key=True)
    passport = models.TextField(unique=True)
    employment_record_number = models.TextField(unique=True)
    snils = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'documents'


class MasterService(models.Model):
    staff = models.ForeignKey('Staff', models.DO_NOTHING, blank=True, null=True)
    service = models.ForeignKey('Service', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_service'
        unique_together = (('staff', 'service'),)


class Position(models.Model):
    position = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'position'


class Staff(models.Model):
    barbershop = models.ForeignKey(Barbershop, models.DO_NOTHING, blank=True, null=True)
    fullname = models.CharField(max_length=60)
    position = models.ForeignKey(Position, models.DO_NOTHING)
    phone = models.TextField(unique=True)
    mail = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'staff'


class Service(models.Model):
    price = models.IntegerField(blank=True, null=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'service'
