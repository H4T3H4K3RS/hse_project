import datetime
from email.mime.image import MIMEImage
from hashlib import sha3_256
from django.contrib.auth.backends import ModelBackend
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth.models import User
import base64
from account.forms import EditForm
from account.models import Profile, Avatar
from app import utils
from app.models import SavedLink, Link, Folder, BotKey


def send_mail(to, subject, template_name, context={}, images=[]):
    context['host'] = settings.HOST
    images = [
        'data:image/png;base64,'
        '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']
    plaintext = get_template(template_name)
    htmly = get_template(template_name)
    subject, from_email, to = subject, settings.EMAIL_HOST_USER, to
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    cnt = 1
    for img in images:
        img = MIMEImage(base64.b64decode(img[img.find(",") + 1:].encode('ascii')), 'jpeg')
        img.add_header('Content-Id', f'<img{cnt}>')
        img.add_header("Content-Disposition", "inline", filename=f"img{cnt}.jpg")
        msg.attach(img)
        cnt += 1
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password.

    """

    def authenticate(self, request, username=None, password=None, **kwars):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def generate_codes(user, date):
    d1 = str(sha3_256(user.username.encode()).hexdigest())
    d2 = str(sha3_256(str(date).encode()).hexdigest())
    d1 = d1 + settings.SECRET_KEY * 4 + d2[:-3]
    d2 = d1 + settings.SECRET_KEY * 4 + d2[:-23]
    d1 = str(sha3_256(d1.encode()).hexdigest())
    d2 = str(sha3_256(d2.encode()).hexdigest())
    return d1, d2


def get_account_context(request, username=None, data_type=1, n=8):
    context = {}
    if data_type == 1:
        s_links = SavedLink.objects.filter(user=request.user)
        if username is None or request.user.username == username:
            context = {
                "bot_api_key": BotKey.objects.get(user=request.user).key,
                'links': Link.objects.filter(folder__user=request.user).order_by("-rating"),
                'user': request.user,
                'saved_links_links': utils.get_saved_links(s_links),
                'saved_links': s_links}
            return context
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        context["bot_api_key"] = BotKey.objects.get(user=request.user).key
        context['user'] = user
        context['links'] = Link.objects.filter(folder__user__username=username, folder__public=True).order_by("-rating")
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
    elif data_type == 2:
        if username is None or request.user.username == username:
            context = {'folders': Folder.objects.filter(user=request.user).order_by("-rating", "public"),
                       'user': request.user, "bot_api_key": BotKey.objects.get(user=request.user).key}
            return context
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        context['user'] = user
        context['folders'] = Folder.objects.filter(user__username=username, public=True).order_by("-rating")
        context["bot_api_key"] = BotKey.objects.get(user=request.user).key
    elif data_type == 3:
        s_links = SavedLink.objects.filter(user=request.user)
        if username is None or request.user.username == username:
            context = {'user': request.user, 'saved_links_links': utils.get_saved_links(s_links),
                       'saved_links': s_links, "bot_api_key": BotKey.objects.get(user=request.user).key}
            return context
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        context['user'] = user
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
        context["bot_api_key"] = BotKey.objects.get(user=request.user).key
    elif data_type == 4:
        s_links = SavedLink.objects.filter(user=request.user)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        context['user'] = user
        context['saved'] = SavedLink.objects.filter(user__username=username)
        context['folders'] = Folder.objects.filter(user__username=username, public=True).order_by("-rating")
        context['links'] = Link.objects.filter(folder__user__username=username, folder__public=True).order_by("-rating")
        context['saved_links_links'] = utils.get_saved_links(s_links)
        context['saved_links'] = s_links
        context['profile'] = Profile.objects.get(user=request.user)
        context['user_profile'] = Profile.objects.get(user=user)
        context["bot_api_key"] = BotKey.objects.get(user=request.user).key
    elif data_type == 5:
        s_links = SavedLink.objects.filter(user=request.user)
        avatars = Avatar.objects.all()
        context = {'saved': SavedLink.objects.filter(user=request.user),
                   'folders': Folder.objects.filter(user=request.user).order_by("public", "-rating"),
                   'links': Link.objects.filter(folder__user=request.user).order_by("-rating"), 'user': request.user,
                   'saved_links': s_links, 'saved_links_links': utils.get_saved_links(s_links),
                   'api_key': BotKey.objects.filter(user=request.user)[0],
                   'form': EditForm(initial={'username': request.user.username}), 'avatars': avatars,
                   "numbers_4": range(n + 1, len(avatars) + 1, n), "profile": Profile.objects.get(user=request.user),
                   "user_profile": Profile.objects.get(user=request.user),
                   "bot_api_key": BotKey.objects.get(user=request.user).key}
    return context


def get_main_context(request, data_type=1, folder_id=None):
    context = {}
    if data_type == 1:
        context = {'links': Link.objects.filter(folder__public=True).order_by("-rating")}
        if request.user.is_authenticated:
            context["profile"] = Profile.objects.get(user=request.user)
            context["bot_api_key"] = BotKey.objects.get(user=request.user).key
            s_links = SavedLink.objects.filter(user=request.user)
            context['saved_links'] = s_links
            context['saved_links_links'] = utils.get_saved_links(s_links)
        else:
            s_links = SavedLink.objects.none()
            context['saved_links'] = s_links
            context['saved_links_links'] = utils.get_saved_links(s_links)
    elif data_type == 2:
        context = {"profile": Profile.objects.get(user=request.user),
                   "bot_api_key": BotKey.objects.get(user=request.user).key}
        s_links = SavedLink.objects.filter(user=request.user)
        queries = request.GET.get('q', None)
        if queries is not None:
            context['value'] = queries
            queries = queries.split()
            q_users = q_folders = q_links = Q()
            for query in queries:
                q_users |= Q(user__username__icontains=query) | Q(user__email__iexact=query)
                q_folders |= Q(name__icontains=query, public=True)
                q_links |= Q(link__icontains=query, folder__public=True)
            users = Profile.objects.filter(q_users)
            folders = Folder.objects.filter(q_folders)
            links = Link.objects.filter(q_links)
        else:
            context['value'] = ""
            users = Profile.objects.order_by("-rating")
            folders = Folder.objects.filter(public=True).order_by("-rating")
            links = Link.objects.filter(folder__public=True).order_by("-rating")
        context['users'] = users
        context['links'] = links
        context['folders'] = folders
        context['saved_links'] = s_links
        context['saved_links_links'] = utils.get_saved_links(s_links)
    elif data_type == 3:
        context = {"profile": Profile.objects.get(user=request.user),
                   "bot_api_key": BotKey.objects.get(user=request.user).key}
        s_links = SavedLink.objects.filter(user=request.user)
        try:
            context['folder'] = Folder.objects.get(id=folder_id)
        except Folder.DoesNotExist:
            return None
        context['links'] = Link.objects.filter(folder_id=folder_id).order_by("-rating")
        context['saved_links_links'] = utils.get_saved_links(s_links)
        context['saved_links'] = s_links
    return context


def social_account_init(backend, user, response, *args, **kwargs):
    try:
        Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user, avatar_id=1)
        profile.save()
        token, code = generate_codes(user, datetime.datetime.now())
        bot_key = BotKey(user=user, chat_id="", key=token)
        bot_key.save()
    return


def check_blacklist(data):
    for word in settings.BLACKLIST:
        if word in data:
            return word
    return None
