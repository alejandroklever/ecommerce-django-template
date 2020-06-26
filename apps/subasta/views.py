import datetime
import threading
from time import sleep

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from apps.subasta.forms import SubastaForm
from apps.subasta.models import SubastaFinalizada, SubastaEnCurso
from apps.tienda.models import Producto, Categoria

mutex = threading.Lock()


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


def listar_subastas_usuario(request):
    user = request.user
    subastas_usuario = SubastaEnCurso.objects.filter(pujante_id=user.id)
    template = loader.get_template("listar_subastas_usuario.html")
    context = {'subastas_usuario': subastas_usuario, 'user': user.username}
    return HttpResponse(template.render(context, request))


def listar_subasta_terminadas(request):
    user = request.user
    subastas_terminada = SubastaFinalizada.objects.filter(tienda__usuario_id=user.id)
    template = loader.get_template("listar_subastas_finalizadas.html")
    context = {'subastas_finalizadas': subastas_terminada, 'user': user.username}
    return HttpResponse(template.render(context, request))


def crear_subasta(request):
    template = loader.get_template('subasta_crear.html')
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            precio = request.POST['precio']
            descripcion = request.POST['descripcion']
            imagen = None
            producto = Producto(nombre=nombre, precio=precio, descripcion=descripcion, imagen=imagen)
            producto.save()
            date, time = request.POST['hora_final'].split('T')
            date = [int(x) for x in date.split('-')]
            time = [int(x) for x in time.split(':')]
            final = datetime.datetime(year=date[0], month=date[1], day=date[2], hour=time[0], minute=time[1])
            tienda = request.user.tienda
            SubastaEnCurso(tienda=tienda, producto=producto, precio_inicial=precio,
                           precio_actual=precio, hora_final=final).save()

            return redirect('tienda:mostrar-tienda')
        except Exception as exc:
            if exc.args[0] == 'User has no tienda.':
                return HttpResponse(template.render({'message': "Necesitas una tienda para poder subastar productos"}))
            return HttpResponse(template.render({'message': "Conjunto de datos Invalido"}, request))
    else:
        return HttpResponse(template.render({}, request))


def busqueda_mostrar_subastas(request):
    try:
        _name = request.GET['prod_name']
    except KeyError:
        _name = ''
    subastas_usuario = SubastaEnCurso.objects.filter(pujante_id=request.user.id)
    subastas_tienda = SubastaEnCurso.objects.filter(tienda__usuario_id=request.user.id)
    template = loader.get_template('buscar_subastas.html')
    results = [elem for elem in SubastaEnCurso.objects.filter(producto__nombre__contains=_name) if
               elem not in subastas_usuario and elem not in subastas_tienda]
    return HttpResponse(template.render({'elems': results}, request))


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
