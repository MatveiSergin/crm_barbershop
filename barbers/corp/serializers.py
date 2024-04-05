from datetime import date, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import Staff, Appointment, Barbershop, Position, Client, Service
from .templates import phonenumber_to_show

class BarbershopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barbershop
        fields = '__all__'

class Staff_serializer(serializers.ModelSerializer):
    barbershop_id = serializers.PrimaryKeyRelatedField(source='barbershop.id', read_only=True)
    position = serializers.CharField(source='position.position')

    class Meta:
        model = Staff
        fields = ['barbershop_id', 'position', 'name', 'surname', 'phone', 'mail']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['phone'] = phonenumber_to_show(data['phone'])
        return data

    def create(self, validated_data):
        #barbershop = Barbershop.objects.get(address=validated_data['barbershop']['address'])
        #validated_data['barbershop'] = barbershop
        position = Position.objects.get(position=validated_data['position']['position'])
        validated_data['position'] = position
        return Staff.objects.create(**validated_data)




class Staff_for_appointment_serializer(serializers.ModelSerializer):
    class Meta:
        model = Staff


        fields = ['name', 'surname']
class Client_for_appointment_serializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'surname', 'phone']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['phone'] = phonenumber_to_show(data['phone'])
        return data



class Service_for_appointment_serializer(serializers.ModelSerializer):
    price = serializers.IntegerField(read_only=True)
    class Meta:
        model = Service
        fields = ['name', 'price']



class Appointment_detail_serializer(serializers.ModelSerializer):
    service = Service_for_appointment_serializer()
    staff = Staff_for_appointment_serializer()
    client = Client_for_appointment_serializer()
    class Meta:
        model = Appointment
        fields = ['data', 'service', 'staff', 'client']


    def create(self, validated_data):
        validated_data['client'] = Client.objects.get(phone=validated_data['client']['phone'])
        validated_data['service'] = Service.objects.get(name=validated_data['service']['name'])
        validated_data['staff'] = Staff.objects.filter(name=validated_data['staff']['name']).filter(surname=validated_data['staff']['surname'])[0]
        return Appointment.objects.create(**validated_data)
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['start_time'] = data['data']
        start_time = map(int, data['data'].split(":"))
        data['end_time'] = (datetime(year=1, month=1, day=1, hour=next(start_time), minute=next(start_time)) + timedelta(minutes=30)).strftime("%H:%M")
        data.pop('data')
        return data

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'price', 'description']