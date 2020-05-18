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


def send_mail(to, subject, template_name, context={}, images=[]):
    context['host'] = settings.HOST
    images = ['data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAL4AAAByCAYAAADtXmtSAAAABGdBTUEAALGPC'
              '/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABmJLR0QA/wD/AP'
              '+gvaeTAAAAB3RJTUUH5AQEFicXel4qwwAAGEVJREFUeNrtnXmcHUWdwL'
              '/V75gjB8nkeD2TcCgxiIooiCuIuC6L64IKqIR5ExTRlUPF9XbR9QDP3RVldwVBoywI84YghxzK4XogiEZQLnGJgYRc82ZyTpKZyet'
              '+r3/7R81k+njnMJM3k1ffz6c/M11dXVVd/XtVv'
              '/rVr6oVDYbTnXoZ8BSg6l2WuiP8Q3J53331LkY9sOpdAIOhHhjBNzQk8XoXYEpgSWMoPp4CqXchpgYNL/gqWSC+eLcW/gOc'
              '/KZZyHDDv3LACL5u6WMC6sAX/Ibo1arE6PiGhsQIvqEhMYJvaEiM4BsaEiP4hobECL6hITGCb2hIjOAbGhIj'
              '+IaGxMzc1orVDDNOgBnHQNPhYM0CcSHfD8NPw+BvYe9f611KQwWM4FdL7CBY8AFYcAEkFoEqUXXeMOz5DWz+Cgz'
              '+nqq9wlpeCfOWV44neSjsAud5GHpc//WG6l070w4j+NXQvBQO+yHMOI6KDi9WC8x+M8w8ATZ9EfqvBLzq8kh9rLZySU73Mlu'
              '+B9tu0OeGqjA6fiVaXg5L74UZryUo9AL5LeCsA3dztNW1ZsLB/wELL2bSvMNUE7S'
              '+Gg69SpcxeUi9a2vaYFr8csTmwmHXatVmHwIDP4Ut18DwU+ANgkpCrA3mvFW32vH5I3Et6Pi81vsH'
              '/1Bj5gJSKH5JWQTbLKV7mMNvgr++DfJb611zUx4j+OVo/yy0vmrsXHKw8XPQ/99EdHe3D7J'
              '/gZ13wEvuHmt9Y7Oh4wuw5kytn1dLbg2sfku0J1FNkOyAWW'
              '+EBRdC8tCxa63HQsdlsP6D9a65KY9RdUrRtATmvycY1v8d2HIlZQese5'
              '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'] + images
    plaintext = get_template(template_name)
    htmly = get_template(template_name)
    subject, from_email, to = subject, settings.EMAIL_HOST_USER, to
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    cnt = 1
    for img in images:
        img = MIMEImage(base64.b64decode(img[img.find(",")+1:].encode('ascii')), 'jpeg')
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
