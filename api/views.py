from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from account.models import Profile
from account.views import handler403, handler404
from app import utils
from app.models import Folder, Link, BotKey, SavedLink


@login_required
def account_view(request, username=None):
    context = {}
    s_links = SavedLink.objects.filter(user=request.user)
    if username is None or request.user.username == username:
        context = {'saved': SavedLink.objects.filter(user=request.user),
                   'folders': Folder.objects.filter(user=request.user).order_by("-rating"),
                   'links': Link.objects.filter(folder__user=request.user).order_by("-rating"), 'owner': 1,
                   'user': request.user,
                   'saved_links_links': utils.get_saved_links(s_links),
                   'saved_links': s_links}
        return render(request, 'api/account.html', context)
    else:
        context['owner'] = 0
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return handler404(request)
    context['user'] = user
    context['saved'] = SavedLink.objects.filter(user__username=username)
    context['folders'] = Folder.objects.filter(user__username=username).order_by("-rating")
    context['links'] = Link.objects.filter(folder__user__username=username).order_by("-rating")
    context['saved_links'] = s_links
    context['saved_links_links'] = utils.get_saved_links(s_links)
    return render(request, 'api/account.html', context)


@login_required
def folder_view(request, folder_id):
    s_links = SavedLink.objects.filter(user=request.user)
    context = {}
    try:
        context['folder'] = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return handler403(request)
    if context['folder'].user == request.user:
        context['owner'] = 1
    else:
        context['owner'] = 0
    context['saved_links'] = s_links
    context['saved_links_links'] = utils.get_saved_links(s_links)
    context['links'] = Link.objects.filter(folder_id=folder_id).order_by("-rating")
    return render(request, 'api/folder.html', context)


def index_view(request):
    context = {'links': Link.objects.order_by("-rating")}
    if request.user.is_authenticated:
        s_links = SavedLink.objects.filter(user=request.user)
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
    else:
        s_links = SavedLink.objects.none()
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
    return render(request, '')


@login_required
def search_view(request):
    context = {}
    s_links = SavedLink.objects.filter(user=request.user)
    queries = request.GET.get('q', None)
    if queries is not None:
        context['value'] = queries
        queries = queries.split()
        q_users = q_folders = q_links = Q()
        for query in queries:
            q_users |= Q(user__username__icontains=query) | Q(user__email__iexact=query)
            q_folders |= Q(name__icontains=query)
            q_links |= Q(link__icontains=query)
        users = Profile.objects.filter(q_users).order_by("-rating")
        folders = Folder.objects.filter(q_folders).order_by("-rating")
        links = Link.objects.filter(q_links).order_by("-rating")
    else:
        context['value'] = ""
        users = Profile.objects.order_by("-rating")
        folders = Folder.objects.order_by("-rating")
        links = Link.objects.order_by("-rating")
    context['users'] = users
    context['links'] = links
    context['folders'] = folders
    context['saved_links'] = s_links
    context['saved_links_links'] = utils.get_saved_links(s_links)
    return render(request, 'api/search.html', context)


@login_required
def account_key_get(request):
    bot_key = BotKey.objects.filter(user=request.user)[0]
    return HttpResponse(bot_key.key)