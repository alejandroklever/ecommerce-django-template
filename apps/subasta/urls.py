from django.contrib.auth.views import login_required
from django.urls import path

from apps.subasta import views

app_name = 'subasta'

urlpatterns = [
    path('listar', views.ListarSubastas.as_view(), name="listar-subastas"),
    path('usuario', views.ListarSubastasUsuario.as_view(), name="listar-subastas-usuario"),
    path('subscripciones', views.ListarSubscripcionesUsuario.as_view(), name='listar-subscripciones'),
    path('detalle/<int:pk>', views.DetallesSubasta.as_view(), name='detalles-subasta'),
    path('crear', views.CrearSubasta.as_view(), name="crear-subasta"),
    path('finalizadas', login_required(views.listar_subasta_terminadas, login_url="usuario:login"),
         name="listar-subastas-finalizadas"),
    path('pujar/<str:pk>', login_required(views.pujar, login_url="usuario:login"), name="pujar")
]
