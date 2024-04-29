import datetime

import jwt
from django.contrib.auth.models import AbstractUser, Group
from django.db import models

from corp.models import Staff


class User(AbstractUser):
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True, verbose_name='Фотография')
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, verbose_name='Информация по сотруднику', null=True, blank=True)

    def get_token(self):
        payload = {
            "id": self.pk,
            "exp": (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp(),
            "iet": datetime.datetime.now().timestamp()
        }

        token = jwt.encode(payload=payload, key='secret', algorithm='HS256')
        return token

    def add_group_by_position(self):
        if self.staff.position.has_accept_appointments:
            group = Group.objects.get(name="Master")
        else:
            group = Group.objects.get(name="Manager")
        group.user_set.add(self)