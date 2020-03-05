"""LaPeseta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('tienda/', include('apps.tienda.urls', namespace='tienda')),
    path('compra/', include('apps.compra.urls', namespace='compra')),
    path('subasta/', include('apps.subasta.urls', namespace='subasta')),
    path('usuario/', include('apps.usuario.urls', namespace='usuario')),
]
