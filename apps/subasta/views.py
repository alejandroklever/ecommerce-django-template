import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.subasta.forms import SubastaCreateForm, SubastaUpdateForm
from apps.subasta.models import SubastaEnCurso
from apps.tienda.models import Producto, Categoria, Tienda


class SubastaListOrderedFilterView(ListView):
    order_fields = {
        'nombre': 'producto__nombre',
        'precio': 'producto__precio',
        'tiempo': 'hora_final',
    }

    def get_queryset(self):
        return SubastaEnCurso.objects.all()

    def filter_query_set(self, query_set):
        query_dict = self.request.GET
        if 'search' in query_dict and query_dict['search']:
            query_set = query_set.filter(producto__nombre__contains=query_dict['search'])

        if 'order_by' in query_dict and query_dict['order_by'] in self.order_fields:
            order_key = self.order_fields[query_dict['order_by']]
            if 'sense' in query_dict and query_dict['sense'] == 'descendente':
                order_key = '-' + order_key
            query_set = query_set.order_by(order_key)

        return query_set

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SubastaListOrderedFilterView, self).get_context_data(**kwargs)

        query_dict = self.request.GET
        context['animate_view'] = 'order_by' not in query_dict and 'search' not in query_dict

        if 'order_by' in query_dict and query_dict['order_by']:
            context['nombre_option'] = query_dict['order_by'] == 'nombre'
            context['precio_option'] = query_dict['order_by'] == 'precio'
            context['cantidad_option'] = query_dict['order_by'] == 'cantidad'

        if 'sense' in query_dict and query_dict['sense']:
            context['asc_option'] = query_dict['sense'] == 'ascendente'
            context['desc_option'] = query_dict['sense'] == 'descendente'

        if 'search' in query_dict and query_dict['search']:
            context['search_value'] = query_dict['search']

        return context


class ActualizarSubasta(UpdateView):
    model = SubastaEnCurso
    form_class = SubastaUpdateForm
    template_name = 'subasta_actualizar.html'
    context_object_name = 'subasta'
    success_url = reverse_lazy('subasta:listar-subscripciones')

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


class CrearSubasta(LoginRequiredMixin, CreateView):
    model = SubastaEnCurso
    form_class = SubastaCreateForm
    template_name = 'subasta_crear.html'

    def post(self, request, *args, **kwargs):
        nombre = request.POST['nombre']
        precio = request.POST['precio']
        descripcion = request.POST['descripcion']
        producto = Producto(nombre=nombre,
                            precio=precio,
                            descripcion=descripcion)
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


class ListaDeSubastasDeTienda(LoginRequiredMixin, SubastaListOrderedFilterView):
    model = SubastaEnCurso
    template_name = 'subastas_tienda_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        tienda_id = self.kwargs.get('tienda_id', 0)
        return self.filter_query_set(SubastaEnCurso.objects.filter(tienda_id=tienda_id))

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


class ListaDeTodasLasSubastas(LoginRequiredMixin, SubastaListOrderedFilterView):
    model = SubastaEnCurso
    template_name = 'subastas_todas_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        return self.filter_query_set(SubastaEnCurso.objects.exclude(tienda__usuario=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tienda_id'] = self.request.user.tienda.id
        context['page_header_text'] = 'Subastas en Curso'
        context['categorias'] = Categoria.objects.all()
        return context


class ListaDeSubastasDeUsuario(LoginRequiredMixin, SubastaListOrderedFilterView):
    template_name = 'subastas_usuario_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        return self.filter_query_set(SubastaEnCurso.objects.filter(tienda__usuario=self.request.user))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListaDeSubastasDeUsuario, self).get_context_data(**kwargs)

        context['page_header_text'] = f'Subastas de {self.request.user.tienda.nombre}'
        context['categorias'] = Categoria.objects.all()

        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id

        return context


class ListaDeSubscripcionesDeUsuario(LoginRequiredMixin, SubastaListOrderedFilterView):
    template_name = 'subastas_subscripciones_listar.html'
    context_object_name = 'subastas'

    def get_queryset(self):
        return self.filter_query_set(SubastaEnCurso.objects.filter(pujante=self.request.user))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListaDeSubscripcionesDeUsuario, self).get_context_data(**kwargs)

        context['page_header_text'] = f'Subscripciones de {self.request.user.tienda.nombre}'
        context['categorias'] = Categoria.objects.all()

        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id

        return context
