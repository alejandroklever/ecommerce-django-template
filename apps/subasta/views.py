import datetime
import threading
from time import sleep

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, FormView

from apps.subasta.forms import SubastaForm
from apps.subasta.models import SubastaFinalizada, SubastaEnCurso
from apps.tienda.models import Producto, Categoria

mutex = threading.Lock()


class CrearSubasta(LoginRequiredMixin, CreateView):
    model = SubastaEnCurso
    form_class = SubastaForm
    template_name = 'subasta_crear.html'
    success_url = reverse_lazy('subasta:listar-subastas-usuario')

    def post(self, request, *args, **kwargs):
        nombre = request.POST['nombre']
        precio = request.POST['precio']
        descripcion = request.POST['descripcion']
        producto = Producto(nombre=nombre, precio=precio, descripcion=descripcion)
        producto.save()

        date, time = request.POST['hora_final'].split('T')
        date = [int(x) for x in date.split('-')]
        time = [int(x) for x in time.split(':')]
        final_datetime = datetime.datetime(year=date[0], month=date[1], day=date[2], hour=time[0], minute=time[1])
        tienda = request.user.tienda
        SubastaEnCurso(tienda=tienda,
                       producto=producto,
                       precio_inicial=precio,
                       precio_actual=precio,
                       hora_final=final_datetime).save()

        return redirect('tienda:mostrar-tienda')


class ListarSubastas(LoginRequiredMixin, ListView):
    model = SubastaEnCurso
    template_name = 'subastas_listar.html'
    context_object_name = 'subastas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tienda_id'] = self.request.user.tienda.id
        context['categorias'] = Categoria.objects.all()
        return context


class ListarSubastasUsuario(LoginRequiredMixin, ListView):
    template_name = 'listar_subastas_usuario.html'
    context_object_name = 'subastas_usuario'

    def get_queryset(self):
        SubastaEnCurso.objects.filter(tienda__usuario=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ListarSubscripcionesUsuario(LoginRequiredMixin, ListView):
    template_name = 'listar_subastas_usuario.html'
    context_object_name = 'subastas_usuario'

    def get_queryset(self):
        SubastaEnCurso.objects.filter(pujante=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class DetallesSubasta(FormView):
    template_name = 'subasta_detalles.html'
    form_class = SubastaForm
    success_url = reverse_lazy('subasta:listar-subastas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tienda_id'] = self.request.user.tienda.id
        context['categorias'] = Categoria.objects.all()
        return context


def listar_subasta_terminadas(request):
    user = request.user
    subastas_terminada = SubastaFinalizada.objects.filter(tienda__usuario_id=user.id)
    template = loader.get_template("listar_subastas_finalizadas.html")
    context = {'subastas_finalizadas': subastas_terminada, 'user': user.username}
    return HttpResponse(template.render(context, request))


def pujar(request, name, precio):
    _precio = float(precio)
    _precio_nuevo = float(request.POST['new_price'])
    if _precio_nuevo <= _precio:
        return HttpResponseRedirect('/subasta/buscar')
    subastas = SubastaEnCurso.objects.filter(precio_actual=precio, producto__nombre=name)
    _subasta = subastas[0]
    _subasta.pujante = request.user
    _subasta.precio_actual = _precio_nuevo
    _prod = _subasta.producto
    _prod.precio = _precio_nuevo
    _prod.save()
    _subasta.save()
    return HttpResponseRedirect('/subasta')


class DestroyerThread(threading.Thread):

    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        while True:
            mutex.acquire()
            now = datetime.datetime.now()
            subastas = SubastaEnCurso.objects.filter(hora_final__lte=now)
            for subasta in subastas:
                if subasta.pujante is not None:
                    SubastaFinalizada(producto=subasta.producto.nombre, tienda=subasta.tienda,
                                      comprador=subasta.pujante,
                                      hora_final=subasta.hora_final, precio_final=subasta.precio_actual).save()
                subasta.delete()
            mutex.release()
            sleep(60)

# a = DestroyerThread(1, "Thread-1", 1)
# a.start()
