from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UsuarioRegistroForm


def recuperar_clave(request):
    return render(request, 'recuperar_clave.html')


class UsuarioRegistro(CreateView):
    model = User
    template_name = 'registrar.html'
    form_class = UsuarioRegistroForm
    success_url = reverse_lazy('usuario:login')
