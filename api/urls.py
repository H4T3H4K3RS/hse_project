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
from django.urls import path
from api import views

urlpatterns = [
    path('account/folder/', views.account_folder, name='account_folder'),
    path('account/<str:username>/folder/', views.account_folder, name='account_folder_username'),
    path('account/links/', views.account_folder, name='account_links'),
    path('account/<str:username>/links/', views.account_links, name='account_links_username'),
    path('account/saved/', views.account_saved, name='account_folder'),
    path('account/<str:username>/saved/', views.account_saved, name='account_saved_username'),
    path('folder/<int:folder_id>/', views.folder_view, name='folder_view'),
    path('index/', views.index_view, name='index_view'),
    path('search/', views.search_view, name='search_view'),
    path('settings/account/key/', views.account_key_get, name='account_key'),
    path('settings/account/avatar/<int:avatar>/', views.account_avatar_set, name='account_avatar'),
]
