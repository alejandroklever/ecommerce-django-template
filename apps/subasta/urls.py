from django.contrib.auth.views import login_required
from django.urls import path

from apps.subasta import views

app_name = 'subasta'

urlpatterns = [
    path('crear', views.CrearSubasta.as_view(), name="crear-subasta"),
    path('listar', views.ListaDeTodasLasSubastas.as_view(), name="listar-subastas-todas"),
    path('usuario', views.ListaDeSubastasDeUsuario.as_view(), name="listar-subastas-usuario"),
    path('<int:tienda_id>/productos', views.ListaDeSubastasDeTienda.as_view(), name="listar-subastas-tienda"),
    path('subscripciones', views.ListaDeSubscripcionesDeUsuario.as_view(), name='listar-subscripciones'),
    path('participar/<int:pk>', views.ActualizarSubasta.as_view(), name='actualizar-subasta'),

    path('finalizadas', login_required(views.listar_subasta_terminadas, login_url="usuario:login"),
         name="listar-subastas-finalizadas"),
    path('pujar/<int:pk>', login_required(views.pujar, login_url="usuario:login"), name="pujar")
]
