import os
from email.mime.image import MIMEImage
from hashlib import sha3_256
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
import base64


class NegativeIntConverter:
    regex = '-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%d' % value


def send_mail(to, subject, template_name, context={}, image_paths=[]):
    context['host'] = settings.HOST
    images = []
    image_paths = ['templates/static/logo.png'] + image_paths
    for path in image_paths:
        with open(path, "rb") as image_file:
            image_b64 = 'data:image/png;base64,' + base64.b64encode(image_file.read()).decode('utf-8')
            images.append(image_b64)
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


def get_saved_links(saved_links):
    res = []
    for saved in saved_links:
        res.append(saved.link)
    return res
