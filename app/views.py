from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
import datetime
from django.http import JsonResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from django.urls import reverse
from django.contrib import messages
import json
from app import utils
from app.forms import AccountSignupForm, AccountLoginForm, LinkAddForm, FolderAddForm
from app.models import Code, Profile, Link, Folder, Vote, SavedLink, BotKey


def handler404(request, exception=None):
    """
    Страница ошибки 404
    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: объект ответа сервера с HTML-кодом внутри
    :rtype: :class:`django.http.HttpResponse`
    """
    return render(request, "errors/404.html", status=404)


def handler403(request, exception=None):
    """
    Страница ошибки 403
    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: объект ответа сервера с HTML-кодом внутри
    :rtype: :class:`django.http.HttpResponse`
    """
    return render(request, "errors/403.html", status=403)


def handler500(request, exception=None):
    """
    Страница ошибки 505
    :param request: объект c деталями запроса
    :type request: :class:`django.http.HttpRequest`
    :return: объект ответа сервера с HTML-кодом внутри
    :rtype: :class:`django.http.HttpResponse`
    """
    return render(request, "errors/500.html", status=500)


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


def account_login(request):
    context = {}
    if request.method == "POST":
        if not request.POST.get("remember_me", None):
            request.session.set_expiry(0)
        form = AccountLoginForm(request.POST)
        if form.is_valid():
            context["form"] = form
            username = form.data["login"]
            password = form.data["password"]
            try:
                username = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    username = User.objects.get(email=username)
                except User.DoesNotExist:
                    messages.error(request, "Имя пользователя/Email неверный")
                    return redirect(reverse('account_login'))
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if username.is_active:
                    login(request, user)
                    return redirect(reverse('link_add'))
                else:
                    messages.error(request,
                                   'На электронную почту, указанную при регистрации было выслано письмо с кодом подтверждения.')
                    return redirect(reverse('account_login'))
            else:
                try:
                    User.objects.get(username=username)
                    messages.error(request, "Неверный пароль")
                except User.DoesNotExist:
                    messages.error(request, "Имя пользователя/Email неверный")
        else:
            messages.error(request, "Неправильный формат данных.")
            context["form"] = AccountLoginForm()
    else:
        context["form"] = AccountLoginForm()
    return render(request, "account/login.html", context)


def account_logout(request):
    logout(request)
    return redirect(reverse('index'))


def account_signup(request):
    context = {}
    if request.method == "POST":
        user_form = AccountSignupForm(request.POST)
        if user_form.is_valid():
            users_email = User.objects.filter(email=user_form.data["email"])
            if len(users_email) != 0:
                messages.error(request, "Пользователь с таким email уже существует.")
                context["form"] = AccountSignupForm(request.POST)
                return render(request, "account/signup.html", context)
            else:
                new_user = user_form.save(commit=True)
                new_user.set_password(user_form.cleaned_data["password1"])
                new_user.is_active = False
                new_user.save()
                profile = Profile(user=new_user)
                profile.save()
                code_object = Code()
                code_object.user = new_user
                code_object.code, code_object.token = utils.generate_codes(new_user, datetime.datetime.now())
                code_object.save()
                mail_context = {'token': code_object.token, 'code': code_object.code, 'user': new_user}
                utils.send_mail(new_user.email, 'Подтверждение Регистрации', 'mail/confirmation.html', mail_context)
                messages.success(request, 'На вашу электронную почту было отправлено письмо, для подтверждения.')
                return redirect(reverse('account_login'))
        else:
            errors = user_form.errors.as_json()
            errors = json.loads(errors)
            codes = []
            for key, message in errors.items():
                for error in message:
                    codes.append(error['code'])
            if 'unique' in codes:
                messages.error(request, "Пользователь с таким именем уже существует.")
            if 'password_too_similar' in codes:
                messages.error(request, "Пароль и имя пользователя совпадают.")
            if 'password_mismatch' in codes:
                messages.error(request, "Пароли не совпадают.")
            if ('password_no_symbol' in codes) or ('password_no_lower' in codes) or ('password_no_upper' in codes) or (
                    'password_no_number' in codes) or ('password_too_short' in codes) or (
                    'password_too_common' in codes):
                messages.error(request, "Пароль не соответствует требованиям. (минимум: длина 8 символов, "
                                        "1 спец.символ, 1 строчная буква, 1 прописная буква, 1 цифра)")
            context["form"] = AccountSignupForm(request.POST)
    else:
        context["form"] = AccountSignupForm()
    return render(request, "account/signup.html", context)


def account_forgot(request):
    return None


def account_recover(request):
    return None


def account_activate(request):
    token = request.GET.get('token', '0')
    code = request.GET.get('code', '0')
    user = request.GET.get('user', '0')
    if token == '0' or code == '0' or user == '0':
        return handler403(request)
    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        return handler404(request)
    try:
        code_object = Code.objects.get(token=token, code=code, user=user)
    except Code.DoesNotExist:
        return handler404(request)
    if datetime.datetime.now(datetime.timezone.utc) - code_object.generated > datetime.timedelta(days=1):
        messages.error(request, 'Истёк срок действия ссылки. Зарегистрируйтесь повторно.')
        code_object.delete()
        Profile.objects.get(user=user).delete()
        links = Link.objects.filter(user=user)
        for i in links:
            i.delete()
        user.delete()
        return redirect(reverse('account_signup'))
    else:
        user.is_active = True
        user.save()
        bot_key = BotKey(user=user, key=code_object.code, chat_id="")
        bot_key.save()
        code_object.delete()
        user = authenticate(request, username=user.username)
        if user is not None:
            login(request, user)
            return redirect(reverse('index'))


@login_required
def account_view(request, username=None):
    context = {}
    s_links = SavedLink.objects.filter(user=request.user)
    if username is None or request.user.username == username:
        context = {'saved': SavedLink.objects.filter(user=request.user),
                   'folders': Folder.objects.filter(user=request.user).order_by("-rating"),
                   'links': Link.objects.filter(folder__user=request.user).order_by("-rating"), 'owner': 1,
                   'user': request.user,
                   'saved_links': s_links,
                   'saved_links_links': utils.get_saved_links(s_links)}
        return render(request, 'account/view.html', context)
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
    context['saved_links_links'] = utils.get_saved_links(s_links)
    context['saved_links'] = s_links
    return render(request, 'account/view.html', context)


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


@login_required
def api_account_view(request, username=None):
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
def api_folder_view(request, folder_id):
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


def api_index_view(request):
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
def api_search_view(request):
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
def account_api_key_get(request):
    bot_key = BotKey.objects.filter(user=request.user)[0]
    return HttpResponse(bot_key.key)
