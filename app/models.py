from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.http import JsonResponse


class Folder(models.Model):
    name = models.CharField(max_length=128)
    rating = models.IntegerField(default=0)


class Link(models.Model):
    link = models.URLField(default="https://google.com")
    folder = models.ForeignKey(to=Folder, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    name = models.CharField(default="Ссылка")
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='owner')
    original = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='original')

    def move(self, user, up):
        if self.owner != user:
            return JsonResponse({'data': "Вы не являетесь владельцем данной ссылки."})
        else:
            try:
                object = self.objects.get(user=self.folder.user, folder=self.folder, rating=self.rating + up)
                object.rating = self.rating
                object.save()
                if self.rating == 100:
                    self.delete()
                elif self.rating != 0:
                    self.rating += up
                    self.save()
            except self.DoesNotExist:
                self.rating += up
                if self.rating == 100:
                    self.delete()
                elif self.rating != 0:
                    self.rating += up
                    self.save()
            return JsonResponse({'data': "Готово."})


class SavedLink(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='saver')
    link = models.URLField(default="https://google.com")
    original = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='owner')


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
