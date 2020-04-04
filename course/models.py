from django.contrib.auth.models import User
from django.db import models
from taggit.managers import TaggableManager
# Create your models here.


class Profile(models.Model):
    type = models.IntegerField(default=1)  # 1 - teacher, 2 - pupil
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    description = models.CharField(default="Описание", max_length=500)
    balance = models.FloatField(default=200)  # 200 rubles present on account creation
    vk = models.URLField(default='')
    instagram = models.URLField(default='')
    telegram = models.URLField(default='')
    facebook = models.URLField(default='')
    website = models.URLField(default='')


class Course(models.Model):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(default='Курс', max_length=100)
    description = models.CharField(default='Нет описания', max_length=500)
    tags = TaggableManager()

