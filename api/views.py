import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from account.models import Profile, Avatar
from account.views import handler404
from app import utils
from account import utils
from app.models import BotKey


@login_required
def account_links(request, username=None):
    context = utils.get_account_context(request, username, 1)
    if context is None:
        return handler404(request)
    return render(request, 'api/account/links.html', context)


@login_required
def account_folder(request, username=None):
    context = utils.get_account_context(request, username, 2)
    if context is None:
        return handler404(request)
    return render(request, 'api/account/folders.html', context)


@login_required
def account_saved(request, username=None):
    context = {}
    if context is None:
        return handler404(request)
    return render(request, 'api/account/saved.html', context)


@login_required
def folder_view(request, folder_id):
    context = utils.get_main_context(request, 3, folder_id)
    return render(request, 'api/folder.html', context)


def index_view(request):
    context = utils.get_main_context(request, 1)
    return render(request, 'api/index.html', context)


@login_required
def search_view(request):
    context = utils.get_main_context(request, 2)
    return render(request, 'api/search.html', context)


@login_required
def account_key_get(request):
    bot_key = BotKey.objects.filter(user=request.user)[0]
    return HttpResponse(bot_key.key)


@login_required
def account_avatar_set(request, avatar):
    try:
        avatar = Avatar.objects.get(name=str(avatar))
    except Avatar.DoesNotExist:
        return JsonResponse({"before": "1.jpg", "after": "1.jpg"}, status=200)
    profile = Profile.objects.get(user=request.user)
    data = {"before": profile.avatar.path}
    profile.avatar = avatar
    profile.save()
    data['after'] = profile.avatar.path
    return JsonResponse(data, status=200)


@login_required
def get_rating(request, username=None):
    context = {}
    if username is None or request.user.username == username:
        context["rating"] = Profile.objects.get(user=request.user).rating
        return JsonResponse(context)
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return handler404(request)
    context["rating"] = Profile.objects.get(user__username=username).rating
    return JsonResponse(context)


@login_required
def update_api_key(request):
    bot_keys = BotKey.objects.filter(user=request.user)
    for bot_key in bot_keys:
        bot_key.delete()
    new_code, token = utils.generate_codes(request.user, datetime.datetime.now())
    new_code = BotKey(key=new_code, user=request.user)
    new_code.save()
    return JsonResponse({"data": new_code.key})
