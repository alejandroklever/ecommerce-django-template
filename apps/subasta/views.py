import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.subasta.forms import SubastaCreateForm, SubastaUpdateForm
from apps.subasta.models import SubastaFinalizada, SubastaEnCurso
from apps.tienda.models import Producto, Categoria, Tienda


class CrearSubasta(LoginRequiredMixin, CreateView):
    model = SubastaEnCurso
    form_class = SubastaCreateForm
    template_name = 'subasta_crear.html'

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

        return redirect('subasta:listar-subastas-usuario')


class ListaDeSubastasDeTienda(LoginRequiredMixin, ListView):
    model = SubastaEnCurso
    template_name = 'subastas_tienda_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        tienda_id = self.kwargs.get('tienda_id', 0)
        return SubastaEnCurso.objects.filter(tienda_id=tienda_id)

    def get_context_data(self, **kwargs):
        context = super(ListaDeSubastasDeTienda, self).get_context_data(**kwargs)

        pk = self.kwargs.get('tienda_id', 0)
        tienda = Tienda.objects.get(id=pk)

        context['tienda'] = tienda
        context['page_header_text'] = f'Subastas de {tienda.nombre}'
        context['categorias'] = Categoria.objects.all()

        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id

        return context


class ListaDeTodasLasSubastas(LoginRequiredMixin, ListView):
    model = SubastaEnCurso
    template_name = 'subastas_todas_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        return SubastaEnCurso.objects.exclude(tienda__usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tienda_id'] = self.request.user.tienda.id
        context['page_header_text'] = 'Subastas en Curso'
        context['categorias'] = Categoria.objects.all()
        return context


class ListaDeSubastasDeUsuario(LoginRequiredMixin, ListView):
    template_name = 'subastas_usuario_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        return SubastaEnCurso.objects.filter(tienda__usuario=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_header_text'] = 'Subastas de ' + str(self.request.user.tienda.nombre)
        context['categorias'] = Categoria.objects.all()

        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id

        return context


class ListaDeSubscripcionesDeUsuario(LoginRequiredMixin, ListView):
    template_name = 'subastas_usuario_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        return SubastaEnCurso.objects.filter(pujante=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ActualizarSubasta(UpdateView):
    model = SubastaEnCurso
    form_class = SubastaUpdateForm
    template_name = 'subasta_actualizar.html'
    context_object_name = 'subasta'
    success_url = reverse_lazy('subasta:listar-subastas-usuario')

    def get_context_data(self, **kwargs):
        context = super(ActualizarSubasta, self).get_context_data(**kwargs)

        context['min_value'] = str(self.get_object().precio_actual).replace(',', '.')
        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id

        return context

    def post(self, request, *args, **kwargs):
        subasta = self.get_object()
        if float(request.POST['precio_actual']) <= subasta.precio_actual:
            return redirect('subasta:actualizar-subasta', subasta.id)

        request.POST = request.POST.copy()
        request.POST['pujante'] = self.request.user
        return super(ActualizarSubasta, self).post(request, *args, **kwargs)


def listar_subasta_terminadas(request):
    user = request.user
    subastas_terminada = SubastaFinalizada.objects.filter(tienda__usuario_id=user.id)
    template = loader.get_template("subastas_finalizadas_listar.html")
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

# a = DestroyerThread(1, "Thread-1", 1)
# a.start()
