"""courrent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from course import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index')
    # path('account/login/', views.account_login, name='account_login'),
    # path('account/logout/', views.account_logout, name='account_logout'),
    # path('account/signup/', views.account_signup, name='account_signup'),
    # path('account/forgot/', views.account_forgot, name='account_forgot'),
    # path('account/recover/<str:code1>/<str:code2>/', views.account_recover, name='account_recover'),
    # path('account/activate/<str:code1>/<str:code2>/', views.account_activate, name='account_activate'),
    # path('account/view/', views.account_view_my, name='account_view_my'),
    # path('account/view/<str:nickname>/', views.account_view_others, name='account_view_others'),
]
