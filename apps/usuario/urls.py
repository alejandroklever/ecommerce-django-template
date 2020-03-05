from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import recuperar_clave, UsuarioRegistro


app_name = 'usuario'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='login.html'), name='logout'),
    path('registrar/', UsuarioRegistro.as_view(), name='registrar'),
    path('recuperar-clave/', recuperar_clave, name='recuperar-clave'),
]
