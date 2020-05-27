from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.http import JsonResponse


class Folder(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


class Link(models.Model):
    link = models.URLField(default="https://google.com")
    folder = models.ForeignKey(to=Folder, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def vote(self, user, state):
        if self.folder.user == user:
            return JsonResponse({'data': "Вы являетесь владельцем данной ссылки."})
        try:
            vote = Vote.objects.get(link=self, user=user)
            if vote.state == 1:
                if state == 1:
                    return JsonResponse({'data': "Вы уже проголосовали за повышение рейтинга ссылки."})
                else:
                    self.rating -= 1
                    self.save()
                    vote.state = 0
                    vote.save()
                    self.folder.rating -= 1
                    self.folder.save()
                    return JsonResponse({'data': "Вы удалили свой голос."})
            elif vote.state == 0:
                if state == 1:
                    self.rating += 1
                    self.save()
                    vote.state = 1
                    vote.save()
                    self.folder.rating += 1
                    self.folder.save()
                    return JsonResponse({'data': "Вы повысили рейтинг ссылки на 1."})
                else:
                    self.rating -= 1
                    self.save()
                    vote.state = -1
                    vote.save()
                    self.folder.rating -= 1
                    self.folder.save()
                    return JsonResponse({'data': "Вы понизили рейтинг ссылки на 1."})
            else:
                if state == 1:
                    self.rating += 1
                    self.save()
                    vote.state = 0
                    vote.save()
                    self.folder.rating += 1
                    self.folder.save()
                    return JsonResponse({'data': "Вы удалили свой голос."})
                else:
                    return JsonResponse({'data': "Вы уже проголосовали за понижение рейтинга ссылки."})
        except Vote.DoesNotExist:
            vote = Vote(link=self, user=user, state=state)
            self.rating += state
            self.save()
            self.folder.rating += state
            self.folder.save()
            vote.save()
            return JsonResponse(
                {'data': "Вы повысили рейтинг ссылки на 1." if state == 1 else "Вы понизили рейтинг ссылки на 1."})


class SavedLink(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='saver')
    link = models.URLField(default="https://google.com")
    original = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='owner')


class Vote(models.Model):
    state = models.IntegerField(default=0)  # 1 - up, -1 - down, 0 - neutral
    link = models.ForeignKey(to=Link, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


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
