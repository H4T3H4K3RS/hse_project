from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse

from account.models import Profile


class Folder(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


class Link(models.Model):
    link = models.URLField(default="https://google.com")
    folder = models.ForeignKey(to=Folder, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def delete(self, using=None, keep_parents=False):
        self.folder.rating -= self.rating
        profile = Profile.objects.get(user=self.folder.user)
        profile.rating -= self.rating
        saved_links = SavedLink.objects.filter(original=self.folder.user, link=self.link)
        for saved_link in saved_links:
            saved_link.original = saved_link.user
            saved_link.save()
        profile.save()
        self.folder.save()
        super().delete(using, keep_parents)

    def vote(self, user, state):
        if self.folder.user == user:
            return JsonResponse({'data': "Вы являетесь владельцем данной ссылки."}, status=202)
        try:
            vote = Vote.objects.get(link=self, user=user)
            if vote.state == 1:
                if state == 1:
                    return JsonResponse({'data': "Вы уже проголосовали за повышение рейтинга ссылки."}, status=208)
                else:
                    self.rating -= 1
                    self.save()
                    vote.state = 0
                    vote.save()
                    self.folder.rating -= 1
                    self.folder.save()
                    profile = Profile.objects.get(user=self.folder.user)
                    profile.rating -= 1
                    profile.save()
                    return JsonResponse({'data': "Вы удалили свой голос."}, status=202)
            elif vote.state == 0:
                if state == 1:
                    self.rating += 1
                    self.save()
                    vote.state = 1
                    vote.save()
                    self.folder.rating += 1
                    self.folder.save()
                    profile = Profile.objects.get(user=self.folder.user)
                    profile.rating += 1
                    profile.save()
                    return JsonResponse({'data': "Вы повысили рейтинг ссылки на 1."}, status=203)
                else:
                    self.rating -= 1
                    self.save()
                    vote.state = -1
                    vote.save()
                    self.folder.rating -= 1
                    self.folder.save()
                    profile = Profile.objects.get(user=self.folder.user)
                    profile.rating -= 1
                    profile.save()
                    return JsonResponse({'data': "Вы понизили рейтинг ссылки на 1."}, status=203)
            else:
                if state == 1:
                    self.rating += 1
                    self.save()
                    vote.state = 0
                    vote.save()
                    self.folder.rating += 1
                    self.folder.save()
                    profile = Profile.objects.get(user=self.folder.user)
                    profile.rating += 1
                    profile.save()
                    return JsonResponse({'data': "Вы удалили свой голос."}, status=202)
                else:
                    return JsonResponse({'data': "Вы уже проголосовали за понижение рейтинга ссылки."}, status=208)
        except Vote.DoesNotExist:
            vote = Vote(link=self, user=user, state=state)
            self.rating += state
            self.save()
            self.folder.rating += state
            self.folder.save()
            vote.save()
            profile = Profile.objects.get(user=self.folder.user)
            profile.rating += state
            profile.save()
            return JsonResponse(
                {'data': "Вы повысили рейтинг ссылки на 1." if state == 1 else "Вы понизили рейтинг ссылки на 1."}, status=203)


class SavedLink(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='saver')
    link = models.URLField(default="https://google.com")
    original = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='owner')


class Vote(models.Model):
    state = models.IntegerField(default=0)  # 1 - up, -1 - down, 0 - neutral
    link = models.ForeignKey(to=Link, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class BotKey(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=64, default="", null=True)
    key = models.CharField(max_length=64)


class BotKeyLanguage(models.Model):
    chat_id = models.CharField(max_length=64, default="")
    lang = models.CharField(max_length=4, default="", null=True)


class BotUnsavedLinks(models.Model):
    chat_id = models.CharField(max_length=64, default="", null=True)
    link = models.URLField(default="")
