from django.contrib.auth.views import login_required
from django.urls import path

import apps.subasta.views as views

app_name = 'subasta'

urlpatterns = [
    path('', login_required(views.subasta_init, login_url="usuario:login"), name="inicio-subasta"),
    path('listar', login_required(views.SubastasListar.as_view(), login_url="usuario:login"), name="listar-subastas"),
    path('usuario', login_required(views.listar_subastas_usuario, login_url="usuario:login"),
         name="listar-subastas-usuario"),
    path('crear', login_required(views.crear_subasta, login_url="usuario:login"), name="crear-subasta"),
    path('buscar', login_required(views.busqueda_mostrar_subastas, login_url="usuario:login"), name="buscar-subastas"),
    path('finalizadas', login_required(views.listar_subasta_terminadas, login_url="usuario:login"),
         name="listar-subastas-finalizadas"),
    path('pujar/<str:name>&<str:precio>', login_required(views.pujar, login_url="usuario:login"), name="pujar")
]
