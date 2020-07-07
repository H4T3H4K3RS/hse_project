from django.contrib.auth.models import User
from django.db import models


class Code(models.Model):
    generated = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=64)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    code = models.CharField(max_length=64)
    status = models.BooleanField(default=0)  # T - activate, 1 - recover


class Avatar(models.Model):
    name = models.IntegerField(default=1)
    path = models.CharField(default="1.jpg", max_length=10)


class Profile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=100)
    avatar = models.ForeignKey(to=Avatar, on_delete=models.CASCADE)
