from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from django.urls import reverse
from django.contrib import messages
from account.models import Profile
from account.views import handler403
from app import utils
from app.forms import LinkAddForm, FolderAddForm
from app.models import Link, Folder, Vote, SavedLink, BotKey


@register.simple_tag
def get_bootstrap_alert_msg_css_name(tags):
    return 'danger' if tags == 'error' else tags


def index(request):
    context = {'links': Link.objects.order_by("-rating")}
    if request.user.is_authenticated:
        s_links = SavedLink.objects.filter(user=request.user)
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
    else:
        s_links = SavedLink.objects.none()
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
    return render(request, 'index.html', context)


@login_required
def search(request):
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
        users = Profile.objects.filter(q_users)
        folders = Folder.objects.filter(q_folders)
        links = Link.objects.filter(q_links)
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
    return render(request, 'search.html', context)


@login_required
def link_add(request):
    context = {}
    if request.method == "POST":
        link_form = LinkAddForm(request.user, request.POST)
        if link_form.is_valid():
            try:
                try:
                    folder = Folder.objects.get(user=request.user, name=link_form.data.get("folder"))
                except Folder.DoesNotExist:
                    messages.error(request, "Подборки не существует.")
                    context["form"] = LinkAddForm(request.user, request.POST)
                    return render(request, "link/add.html", context)
                link = Link.objects.get(link=link_form.data.get("link"), folder=folder)
                messages.error(request, "Вы уже сохранили данную ссылку.")
                return redirect('link_add')
            except Link.DoesNotExist:
                folder = Folder.objects.get(user=request.user, name=link_form.data.get("folder"))
                link = Link(link=link_form.data.get("link"), folder=folder)
                link.save()
                messages.success(request, "Ссылка добавлена")
                return redirect(reverse('folder_view', kwargs={"folder_id": folder.id}))

        else:
            messages.error(request, "Неправильные ссылка")
            context["form"] = LinkAddForm(request.user, request.POST)
    else:
        context["form"] = LinkAddForm(request.user)
        folders = Folder.objects.filter(user=request.user)
        if len(folders) == 0:
            messages.error(request, "Для начала, создайте подборку.")
            return redirect(reverse('folder_add'))
    return render(request, "link/add.html", context)


@login_required
def link_vote(request, link_id, state):
    try:
        link = Link.objects.get(id=link_id)
        return link.vote(request.user, state)
    except Link.DoesNotExist:
        return JsonResponse({'data': "Ссылка не существует"})


@login_required
def link_edit(request, link_id):
    context = {}
    if request.method == "POST":
        link_form = LinkAddForm(request.user, request.POST)
        if link_form.is_valid():
            try:
                try:
                    folder = Folder.objects.get(user=request.user, name=link_form.data.get("folder"))
                except Folder.DoesNotExist:
                    messages.error(request, "Подборки не существует.")
                    return redirect(reverse("folder_add"))
                link = Link.objects.get(id=link_id)
                try:
                    link_in_folder = Link.objects.get(link=link.link, folder=folder)
                    messages.error(request, "Ссылка уже была добавлена в данную подборку.")
                    return redirect(reverse('link_edit', kwargs={"link_id": link_in_folder.id}))
                except Link.DoesNotExist:
                    pass
                link.folder = folder
                if link.link != link_form.data.get("link"):
                    link.link = link_form.data.get("link")
                    link.folder.rating -= link.rating
                    link.rating = 0
                    link.save()
                    link_votes = Vote.objects.filter(link=link)
                    for vote in link_votes:
                        vote.delete()
                link.save()
                messages.success(request, "Изменения сохранены")
                return redirect(reverse('folder_view', kwargs={"folder_id": folder.id}))
            except Link.DoesNotExist:
                messages.error(request, "Ссылка не существует или вы не являетесь её владельцем")
                return redirect(reverse('link_add'))

        else:
            messages.error(request, "Неправильные ссылка")
            context["form"] = LinkAddForm(request.user, request.POST)
    else:
        try:
            link = Link.objects.get(id=link_id)
            if link.folder.user != request.user:
                return handler403(request)
            context['link'] = link
            context["form"] = LinkAddForm(request.user, initial={"folder": [link.folder.name], 'link': link.link})
        except Link.DoesNotExist:
            messages.error(request, 'Ссылка не существует')
            return redirect(reverse('link_add'))
    return render(request, "link/edit.html", context)


@login_required
def link_delete(request, link_id):
    try:
        link = Link.objects.get(id=link_id)
        folder = link.folder
        folder.rating -= link.rating
        folder.save()
        if link.folder.user != request.user:
            return JsonResponse({"data": "Ссылка вам не принадлежитп."})
        link_votes = Vote.objects.filter(link=link)
        for vote in link_votes:
            vote.delete()
        link.delete()
        return JsonResponse({"data": "Ссылка удалена."})
    except Link.DoesNotExist or Folder.DoesNotExist:
        return JsonResponse({"data": "Ссылка или подборка не существуют."})


@login_required
def favourite_save_saved(request, link_id):
    try:
        link = SavedLink.objects.get(id=link_id)
        try:
            saved_link = SavedLink.objects.get(link=link.link, user=request.user)
            data = 'Ссылка уже сохранена'
        except SavedLink.DoesNotExist:
            saved_link = SavedLink(link=link.link, user=request.user, original=link.original)
            saved_link.save()
            try:
                original_link = Link.objects.get(folder__user=saved_link.original, link=link.link)
                original_link.rating += 1
                original_link.folder.rating += 1
                original_link.folder.save()
                original_link.save()
            except Link.DoesNotExist:
                pass
            data = "Ссылка сохранена."
    except SavedLink.DoesNotExist:
        data = "Ссылка не существует"
    return JsonResponse({"data": data}, content_type="application/json")


@login_required
def favourite_save(request, link_id):
    try:
        link = Link.objects.get(id=link_id)
        try:
            saved_link = SavedLink.objects.get(link=link.link, user=request.user)
            data = 'Ссылка уже сохранена'
        except SavedLink.DoesNotExist:
            saved_link = SavedLink(link=link.link, user=request.user, original=link.folder.user)
            if saved_link.original != request.user:
                link.rating += 1
                link.folder.rating += 1
                link.folder.save()
                link.save()
            saved_link.save()
            data = "Ссылка сохранена."
    except Link.DoesNotExist:
        data = "Ссылка не существует"
    return JsonResponse({"data": data}, content_type="application/json")


@login_required
def favourite_delete(request, link_id):
    try:
        saved_link = SavedLink.objects.get(id=link_id)
        if saved_link.original != request.user:
            try:
                link = Link.objects.get(folder__user=saved_link.original, link=saved_link.link)
                link.rating -= 1
                link.folder.rating -= 1
                link.folder.save()
                link.save()
            except Link.DoesNotExist:
                pass
        saved_link.delete()
        data = "Ссылка удалена."
    except SavedLink.DoesNotExist:
        data = "Ссылка не существует или вам не принадлежит"
    return JsonResponse({"data": data})


@login_required
def folder_add(request):
    context = {}
    if request.method == "POST":
        folder_form = FolderAddForm(request.POST)
        if folder_form.is_valid():
            try:
                folder = Folder.objects.get(name=folder_form.data['name'], user=request.user)
                messages.error(request, "Вы уже создали данную подборку.")
                context["form"] = FolderAddForm(request.POST)
                return render(request, "folder/add.html", context)
            except Folder.DoesNotExist:
                folder = Folder(name=folder_form.data['name'], user=request.user)
                folder.save()
                messages.success(request, "Подборка создана")
                return redirect(reverse('link_add'))
        else:
            messages.error(request, f"Неправильные данные")
            context["form"] = FolderAddForm(request.POST)
    else:
        context["form"] = FolderAddForm()
    return render(request, "folder/add.html", context)


@login_required
def folder_view(request, folder_id):
    context = {}
    s_links = SavedLink.objects.filter(user=request.user)
    try:
        context['folder'] = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return handler403(request)
    if context['folder'].user == request.user:
        context['owner'] = 1
    else:
        context['owner'] = 0
    context['links'] = Link.objects.filter(folder_id=folder_id).order_by("-rating")
    context['saved_links_links'] = utils.get_saved_links(s_links)
    context['saved_links'] = s_links
    return render(request, 'folder/view.html', context)


@login_required
def folder_edit(request, folder_id):
    context = {}
    if request.method == "POST":
        folder_form = FolderAddForm(request.POST)
        if folder_form.is_valid():
            try:
                context['folder'] = folder = Folder.objects.get(id=folder_id, user=request.user)
                folder.name = folder_form.data.get("name")
                folder.save()
                messages.success(request, "Подборка изменена")
                context["form"] = FolderAddForm(request.POST)
                return render(request, "folder/edit.html", context)
            except Folder.DoesNotExist:
                return handler403(request)
        else:
            messages.error(request, f"Неправильные данные")
            try:
                context['folder'] = folder = Folder.objects.get(id=folder_id, user=request.user)
                context["form"] = FolderAddForm(initial={'name': folder.name})
            except Folder.DoesNotExist:
                return handler403(request)
    else:
        try:
            context['folder'] = folder = Folder.objects.get(id=folder_id, user=request.user)
        except Folder.DoesNotExist:
            return handler403(request)
        context["form"] = FolderAddForm(initial={'name': folder.name})
    return render(request, "folder/edit.html", context)


@login_required
def folder_delete(request, folder_id):
    try:
        folder = Folder.objects.get(id=folder_id)
        for link in Link.objects.filter(folder=folder):
            link_votes = Vote.objects.filter(link=link)
            for vote in link_votes:
                vote.delete()
            link.delete()
        folder.delete()
        return JsonResponse({'data': 'Подборка удалена.'})
    except Folder.DoesNotExist:
        return JsonResponse({"data": "Подборка вам не существует."})
