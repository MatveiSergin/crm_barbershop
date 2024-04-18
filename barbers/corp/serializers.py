from datetime import date, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import Staff, Appointment, Barbershop, Position, Client, Service, MasterService
from .templates import phonenumber_to_show, phonenumber_to_db


class BarbershopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    class Meta:
        model = Barbershop
        fields = ['id', 'city', 'street']
        read_only_fields = ['city', 'street']

class StaffSerializerForInfo(serializers.ModelSerializer):
    class Meta:
        model = Staff


        fields = ['id', 'name', 'surname']




class Client_for_appointment_serializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'surname', 'phone']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['phone'] = phonenumber_to_show(data['phone'])
        return data
class ServiceSerializerForInfo(serializers.ModelSerializer):
    price = serializers.IntegerField(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'name', 'price']



class Appointment_detail_serializer(serializers.ModelSerializer):
    service = ServiceSerializerForInfo()
    staff = StaffSerializerForInfo()
    client = Client_for_appointment_serializer()
    class Meta:
        model = Appointment
        fields = ['id', 'data', 'service', 'staff', 'client']


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
    staff = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'description', 'staff']

    def get_staff(self, obj):
        staff_services = MasterService.objects.filter(service=obj)
        staff_serializer = MasterServiceSerializerForStaff(staff_services, many=True)
        return staff_serializer.data

class MasterServiceSerializerForStaff(serializers.ModelSerializer):
    staff = StaffSerializerForInfo()
    class Meta:
        model = MasterService
        fields = ['staff']


class StaffSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    barbershop = BarbershopSerializer()
    position = serializers.CharField(source='position.position')
    class Meta:
        model = Staff
        fields = ['id', 'barbershop', 'name', 'surname', 'patronymic', 'position', 'phone', 'mail', 'services']

    def get_services(self, obj):
        if obj.position.has_accept_appointments:
            master_services = MasterService.objects.filter(staff=obj)
            serializer = MasterServiceSerializerForService(master_services, many=True)
            return serializer.data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['phone'] = phonenumber_to_show(data['phone'])
        return data

    def create(self, validated_data):
        barbershop = validated_data.pop('barbershop', None)
        if 'pk' in barbershop:
            validated_data['barbershop'] = Barbershop.objects.get(pk=barbershop['pk'])

        validated_data['position'] = Position.objects.get(position=validated_data['position']['position'])

        return Staff.objects.create(**validated_data)

    def update(self, instance, validated_data):
        barbershop = validated_data.pop('barbershop', None)
        if barbershop:
            instance.barbershop = Barbershop.objects.get(pk=barbershop['pk'])
        position = validated_data.pop('position', None)
        if position:
            instance.position = Position.objects.get(position=position['position'])

        name = validated_data.pop('name', None)
        if name is not None:
            instance.name = name
        surname = validated_data.pop('surname', None)
        if surname is not None:
            instance.surname = surname
        patronymic = validated_data.pop('patronymic', None)
        if patronymic is not None:
            instance.patronymic = patronymic
        mail = validated_data.pop('mail', None)
        if mail is not None:
            instance.mail = mail
        phone = validated_data.pop('phone', None)
        if phone is not None:
            instance.phone = phone

        instance.save()
        return instance





class MasterServiceSerializerForService(serializers.ModelSerializer):
    service = ServiceSerializerForInfo()
    class Meta:
        model = MasterService
        fields = ['service']

class FreeTimeSerializer(serializers.Serializer):
    serializers.ListField(child=serializers.CharField())



