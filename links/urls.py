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
from django.contrib import admin
from django.urls import path, register_converter, include
from js_urls.views import JsUrlsView
from app import views, utils
from account.views import handler404 as generic_handler404
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

register_converter(utils.NegativeIntConverter, 'int')
handler404 = 'account.views.handler404'
handler403 = 'account.views.handler403'
handler500 = 'account.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    url(r'^account/', include(('account.urls', 'account'), namespace="account")),
    path('favourite/save/<int:link_id>/', views.favourite_save, name='favourite_save'),
    path('favourite/save_alt/<int:link_id>/', views.favourite_save_saved, name='favourite_save_alt'),
    path('favourite/delete/<int:link_id>/', views.favourite_delete, name='favourite_delete'),
    path('link/add/', views.link_add, name='link_add'),
    # path('link/view/<int:link_id>/', views.link_view, name='link_view'),
    path('link/edit/<int:link_id>/', views.link_edit, name='link_edit'),
    path('link/delete/<int:link_id>/', views.link_delete, name='link_delete'),
    path('link/<int:link_id>/vote/<int:state>/', views.link_vote, name='link_vote'),
    path('folder/add/', views.folder_add, name='folder_add'),
    path('folder/view/<int:folder_id>/', views.folder_view, name='folder_view'),
    path('folder/edit/<int:folder_id>/', views.folder_edit, name='folder_edit'),
    path('folder/delete/<int:folder_id>/', views.folder_delete, name='folder_delete'),
    url(r'^api/', include(('api.urls', 'api'), namespace="api")),
    url(r'^get-urls/$', JsUrlsView.as_view(), name='js_urls'),
    url(r'^(?P<exception>.*)/$', generic_handler404, name="page_404"),
]
urlpatterns += staticfiles_urlpatterns()
