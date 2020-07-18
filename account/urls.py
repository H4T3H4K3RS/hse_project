"""links URL Configuration

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
from django.conf.urls import url
from django.urls import path, include
from account import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('forgot/', views.forgot, name='forgot'),
    path('recover/', views.recover, name='recover'),
    path('activate/', views.activate, name='activate'),
    path('view/', views.view, name='view_my'),
    path('view/<str:username>/', views.view, name='view_others'),
    path('agreement/', views.agreement, name='agreement'),
    path('delete/', views.delete, name='delete'),
    # url(r'', include('social_django.urls', namespace='social'))
]
