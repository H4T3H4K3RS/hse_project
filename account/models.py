from django.contrib.auth.models import User
from django.db import models


class Code(models.Model):
    generated = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=64)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    code = models.CharField(max_length=64)
    activate = models.BooleanField(default=0)  # 0 - activate, 1 - recover


class Profile(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=100)
    # description = models.CharField(default="Описание", max_length=500)
