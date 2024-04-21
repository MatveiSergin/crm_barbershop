from django.contrib.auth.models import AbstractUser
from django.db import models

from corp.models import Staff


class User(AbstractUser):
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True, verbose_name='Фотография')
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, verbose_name='Информация по сотруднику', null=True, blank=True)
