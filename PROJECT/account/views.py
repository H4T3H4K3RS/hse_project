import datetime
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from account.forms import LoginForm, SignupForm, RecoverForm, NewPasswordForm, EditForm
from account.models import Profile, Code
from account.utils import check_blacklist
from app import utils
from account import utils
from app.models import SavedLink, BotKey


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


def login(request):
    context = {}
    if request.method == "POST":
        next_page = request.POST.get('next', None)
        if not request.POST.get("remember_me", None):
            request.session.set_expiry(0)
        form = LoginForm(request.POST)
        if form.is_valid():
            context["form"] = form
            username = form.data["login"]
            password = form.data["password"]
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    messages.error(request, "Имя пользователя/Email неверный")
                    return redirect(reverse('account:login'))
            if user.check_password(password):
                if user.is_active:
                    user_auth = authenticate(request, username=user.username)
                    auth_login(request, user_auth)
                    messages.success(request, f'Здравствуйте, {user.username}')
                    if next_page is not None:
                        return redirect(next_page)
                    return redirect(reverse('link_add'))
                else:
                    try:
                        code_object = Code.objects.get(user=user, status=True)
                        messages.warning(request, 'Был получен запрос на восстановление пароля. Учётная запись деактивирована. Следуйте инструкциями отправленным на электронную почту, указанную при регистрации.')
                    except Code.DoesNotExist:
                        messages.error(request, "На электронную почту, указанную при регистрации было выслано письмо с инструкцией для подтверждения аккаунта.")
            else:
                try:
                    User.objects.get(username=username)
                    messages.error(request, "Неверный пароль")
                except User.DoesNotExist:
                    messages.error(request, "Имя пользователя/Email неверный")
        else:
            messages.error(request, "Неправильный формат данных.")
            context["form"] = LoginForm()
    else:
        if request.user.is_authenticated:
            messages.warning(request, "Вы уже вошли в аккаунт.")
            return redirect(reverse('account:view_my'))
        next_page = request.GET.get('next', None)
        context['next'] = next_page
        context["form"] = LoginForm()
    return render(request, "account/login.html", context)


def logout(request):
    messages.success(request, f"До скорых встреч, {request.user.username}")
    auth_logout(request)
    return redirect(reverse('index'))


def signup(request):
    context = {}
    if request.method == "POST":
        user_form = SignupForm(request.POST)
        if user_form.is_valid():
            users_email = User.objects.filter(email=user_form.data["email"])
            if len(users_email) != 0:
                messages.error(request, "Пользователь с таким email уже существует.")
                context["form"] = SignupForm(request.POST)
                return render(request, "account/signup.html", context)
            else:
                ok = check_blacklist(user_form.data['email'])
                if ok is not None:
                    messages.error(request, f"Имя пользователя не должно содержать \"{ok}\"")
                    context["form"] = SignupForm(request.POST)
                    return render(request, "account/signup.html", context)
                else:
                    new_user = user_form.save(commit=True)
                    new_user.set_password(user_form.cleaned_data["password1"])
                    new_user.is_active = False
                    new_user.save()
                    profile = Profile(user=new_user, avatar_id=1)
                    profile.save()
                    code_object = Code()
                    code_object.user = new_user
                    code_object.code, code_object.token = utils.generate_codes(new_user, datetime.datetime.now())
                    code_object.save()
                    mail_context = {'token': code_object.token, 'code': code_object.code, 'user': new_user}
                    utils.send_mail(new_user.email, 'Подтверждение Регистрации', 'mail/confirmation.html', mail_context)
                    messages.warning(request, 'На вашу электронную почту было отправлено письмо, для подтверждения.')
                    return redirect(reverse('account:login'))
        else:
            errors = user_form.errors.as_json()
            errors = json.loads(errors)
            codes = []
            for key, message in errors.items():
                for error in message:
                    codes.append(error['code'])
            print(codes)
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
            context["form"] = SignupForm(request.POST)
    else:
        if request.user.is_authenticated:
            messages.warning(request, "Вы уже вошли в аккаунт.")
            return redirect(reverse('account:view_my'))
        context["form"] = SignupForm()
    return render(request, "account/signup.html", context)


def forgot(request):
    context = {}
    if request.method == "POST":
        form = RecoverForm(request.POST)
        if form.is_valid():
            users = User.objects.filter(email=form.data["email"])
            if len(users) != 0:
                user = users[0]
                try:
                    code_object = Code.objects.get(user=user, status=False)
                    flag = True
                except Code.DoesNotExist:
                    code_object = Code()
                    flag = False
                if user.is_active or flag:
                    code_object.user = user
                    code_object.code, code_object.token = utils.generate_codes(user, datetime.datetime.now())
                    code_object.status = True
                    code_object.save()
                    code_object.user.is_active = False
                    code_object.user.save()
                    mail_context = {'token': code_object.token, 'code': code_object.code, 'user': user}
                    utils.send_mail(user.email, 'Восстановление Пароля', 'mail/recovery.html', mail_context)
                    messages.warning(request, 'Инструкция по восстановлению пароля отправлена на почту.')
                    return redirect(reverse('account:login'))
                else:
                    try:
                        code_object = Code.objects.get(user=user)
                        code_object.delete()
                    except Code.DoesNotExist:
                        pass
                    code_object = Code()
                    code_object.user = user
                    code_object.code, code_object.token = utils.generate_codes(user, datetime.datetime.now())
                    code_object.save()
                    mail_context = {'token': code_object.token, 'code': code_object.code, 'user': user}
                    utils.send_mail(user.email, 'Подтверждение Регистрации', 'mail/confirmation.html', mail_context)
                    messages.warning(request, 'Аккаунт не был активирован, поэтому письмо для подтверждения регистрации было повторно отправлено на почту.')
            else:
                messages.error(request, 'Пользователя с таким email не существует')
        else:
            messages.error("Проблемы с ReCaptcha")
        context["form"] = RecoverForm(request.POST)
    else:
        if request.user.is_authenticated:
            messages.warning(request, "Вы уже вошли в аккаунт.")
            return redirect(reverse('account:view_my'))
        context["form"] = RecoverForm()
    return render(request, "account/forgot.html", context)


def recover(request):
    context = {}
    if request.method == "POST":
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            token = form.data['token']
            code = form.data['code']
            user = form.data['user']
            if token == '0' or code == '0' or user == '0':
                return handler403(request)
            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return handler404(request)
            try:
                code_object = Code.objects.get(token=token, code=code, user=user, status=True)
            except Code.DoesNotExist:
                return handler404(request)
            if datetime.datetime.now(datetime.timezone.utc) - code_object.generated > datetime.timedelta(days=1):
                messages.error(request, 'Истёк срок действия ссылки. Отправьте запрос на восстановление повторно.')
                code_object.delete()
                return redirect(reverse('account:forgot'))
            else:
                user.is_active = True
                user.set_password(form.cleaned_data["password1"])
                user.save()
                code_object.delete()
                user = authenticate(request, username=user.username)
                if user is not None:
                    auth_login(request, user)
                return redirect(reverse('index'))
        else:
            errors = form.errors.as_json()
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
            context["form"] = NewPasswordForm(request.POST)
    else:
        if request.user.is_authenticated:
            messages.warning(request, "Вы уже вошли в аккаунт.")
            return redirect(reverse('account:view_my'))
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
            code_object = Code.objects.get(token=token, code=code, user=user, status=True)
        except Code.DoesNotExist:
            return handler404(request)
        if datetime.datetime.now(datetime.timezone.utc) - code_object.generated > datetime.timedelta(days=1):
            messages.error(request, 'Истёк срок действия ссылки. Отправьте запрос на восстановление повторно.')
            code_object.delete()
            return redirect(reverse('account:forgot'))
        else:
            form = NewPasswordForm(
                initial={'user': user.username, 'token': code_object.token, 'code': code_object.code})
            context['form'] = form
    return render(request, "account/restore.html", context=context)


def activate(request):
    if request.user.is_authenticated:
        messages.warning(request, "Вы уже вошли в аккаунт.")
        return redirect(reverse('account:view_my'))
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
        user.delete()
        return redirect(reverse('account:signup'))
    else:
        user.is_active = True
        user.save()
        bot_key = BotKey(user=user, key=code_object.code, chat_id="")
        bot_key.save()
        code_object.delete()
        user = authenticate(request, username=user.username)
        if user is not None:
            auth_login(request, user)
            return redirect(reverse('index'))


@login_required
def view(request, username=None):
    if request.user.username == username:
        return redirect(reverse("account:view_my"))
    if username is None:
        context = utils.get_account_context(request, username, 5)
        if request.method == "POST":
            form = EditForm(request.POST)
            if form.is_valid() or (form.data['password1'] == "" and form.data['password2'] == ""):
                if form.data['username'] != request.user.username:
                    try:
                        User.objects.get(username=form.data['username'])
                        messages.error(request, "Пользователь с выбранным именем уже существует.")
                        context["form"] = EditForm(initial={'username': form.data['username']})
                        return render(request, 'account/view.html', context)
                    except User.DoesNotExist:
                        ok = check_blacklist(form.data['username'])
                        if ok is None:
                            messages.success(request, "Имя пользователя успешно изменено.")
                            request.user.username = form.data['username']
                            request.user.save()
                        else:
                            messages.error(request, f"Имя пользователя не должно содержать \"{ok}\"")
                if form.data['password1'] != "" and form.data['password2'] != "":
                    request.user.set_password(form.cleaned_data['password1'])
                    request.user.save()
                    messages.success(request, "Пароль был изменён.")
                user_auth = authenticate(request, username=form.data['username'])
                auth_login(request, user_auth)
            else:
                errors = form.errors.as_json()
                errors = json.loads(errors)
                codes = []
                for key, message in errors.items():
                    for error in message:
                        codes.append(error['code'])
                if 'password_too_similar' in codes:
                    messages.error(request, "Пароль и имя пользователя совпадают.")
                if 'password_mismatch' in codes:
                    messages.error(request, "Пароли не совпадают.")
                if ('password_no_symbol' in codes) or ('password_no_lower' in codes) or (
                        'password_no_upper' in codes) or (
                        'password_no_number' in codes) or ('password_too_short' in codes) or (
                        'password_too_common' in codes):
                    messages.error(request, "Пароль не соответствует требованиям. (минимум: длина 8 символов, "
                                            "1 спец.символ, 1 строчная буква, 1 прописная буква, 1 цифра)")
        return render(request, 'account/view.html', context)
    context = utils.get_account_context(request, username, 4)
    if context is None:
        return handler404(request)
    return render(request, 'account/view.html', context)


def agreement(request):
    context = {}
    context['host'] = settings.HOST
    return render(request, "account/agreement.html", context)


@login_required
def delete(request):
    context = {}
    saved_links = SavedLink.objects.filter(original=request.user)
    for saved_link in saved_links:
        saved_link.original = saved_link.user
        saved_link.save()
    messages.success(request, f"Аккаунт {request.user} успешно удалён. До скорых встреч 👋")
    request.user.delete()
    return redirect(reverse("index"))
