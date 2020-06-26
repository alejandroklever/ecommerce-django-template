from django.contrib.auth.views import login_required
from django.urls import path

from apps.subasta.views import (ListarSubastas, ListarSubscripcionesUsuario, ListarSubastasUsuario,
                                crear_subasta, busqueda_mostrar_subastas, listar_subasta_terminadas,
                                pujar)

app_name = 'subasta'

urlpatterns = [
    path('listar', ListarSubastas.as_view(), name="listar-subastas"),
    path('usuario', ListarSubastasUsuario.as_view(), name="listar-subastas-usuario"),
    path('subscripciones', ListarSubscripcionesUsuario.as_view(), name='listar-subscripciones'),
    path('crear', login_required(crear_subasta, login_url="usuario:login"), name="crear-subasta"),
    path('buscar', login_required(busqueda_mostrar_subastas, login_url="usuario:login"), name="buscar-subastas"),
    path('finalizadas', login_required(listar_subasta_terminadas, login_url="usuario:login"),
         name="listar-subastas-finalizadas"),
    path('pujar/<str:name>&<str:precio>', login_required(pujar, login_url="usuario:login"), name="pujar")
]
