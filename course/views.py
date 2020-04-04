from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'account/login.html')


def account_login():
    pass

