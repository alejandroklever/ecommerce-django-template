from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, FormView

from apps.tienda.forms import ActualizarTiendaForm, ProductoForm, StockForm
from apps.tienda.models import Tienda, Producto, Stock, Categoria


class StockListOrderedFilterView(ListView):
    order_fields = {
        'nombre': 'producto__nombre',
        'precio': 'producto__precio',
        'cantidad': 'cantidad',
    }

    def get_queryset(self):
        return Stock.objects.all()

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
        context = super(StockListOrderedFilterView, self).get_context_data(**kwargs)

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


class ListaDeTiendas(ListView):
    """
    Lista de todas las tiendas existentes excepto la del propio usuario
    """
    model = Tienda
    template_name = 'tiendas_listar.html'
    context_object_name = 'tiendas'

    def get_queryset(self):
        return Tienda.objects.exclude(usuario_id=self.request.user.id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id
        return context


class ListaDeProductos(StockListOrderedFilterView):
    """
    Lista de todos productos existentes
    """
    template_name = 'productos_listar.html'
    context_object_name = 'stock_list'

    def get_queryset(self):
        return self.filter_query_set(Stock.objects.exclude(tienda__usuario_id=self.request.user.id))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_header_text'] = 'Productos'
        context['categorias'] = Categoria.objects.all()
        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id
        return context


class VisitarTienda(StockListOrderedFilterView):
    """
    Muestra los productos de la tienda especificada por el parametro pk
    """
    template_name = 'tienda_visitar.html'

    def get_queryset(self):
        tienda_id = self.kwargs.get('tienda_id', 0)
        return self.filter_query_set(Stock.objects.filter(tienda_id=tienda_id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tienda_id = self.kwargs.get('tienda_id', 0)

        context['tienda'] = Tienda.objects.get(id=tienda_id)
        context['page_header_text'] = f'Bienvenid@ a {context["tienda"]}'
        context['categorias'] = Categoria.objects.all()

        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id

        return context


# noinspection PyAttributeOutsideInit
class MostrarTienda(LoginRequiredMixin, StockListOrderedFilterView):
    template_name = 'tienda_usuario_mostrar.html'
    context_object_name = 'user_stock_list'

    def get_queryset(self):
        self.user = self.request.user

        try:
            self.user.tienda
        except ObjectDoesNotExist:
            # Creamos una tienda por defecto
            self.user.tienda = Tienda(nombre=f'Tienda de {self.user}', usuario=self.user)
            self.user.tienda.save()

        return self.filter_query_set(Stock.objects.filter(tienda__usuario_id=self.user.id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tienda_id'] = self.user.tienda.id
        context['page_header_text'] = 'Administracion de ' + str(self.user.tienda)
        context['categorias'] = Categoria.objects.all()
        return context


# noinspection PyAttributeOutsideInit
class EditarTienda(LoginRequiredMixin, UpdateView):
    model = Tienda
    template_name = 'tienda_usuario_editar.html'
    form_class = ActualizarTiendaForm
    success_url = reverse_lazy('tienda:mostrar-tienda')
    context_object_name = 'tienda'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tienda_id'] = self.request.user.tienda.id
        return context


# noinspection PyAttributeOutsideInit
class CrearProducto(FormView):
    model = Stock
    template_name = 'producto_form.html'
    form_class = StockForm
    second_form_class = ProductoForm
    success_url = reverse_lazy('tienda:mostrar-tienda')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Crear'
        context['header'] = 'Agregue su producto'
        if not isinstance(self.request.user, AnonymousUser):
            context['tienda_id'] = self.request.user.tienda.id
        if 'form_stock' not in context:
            context['form_stock'] = self.form_class(self.request.GET)
        if 'form_producto' not in context:
            context['form_producto'] = self.second_form_class(self.request.GET)
        return context

    def post(self, request, *args, **kwargs):
        form_stock = self.form_class(request.POST)
        form_producto = self.second_form_class(request.POST)

        if form_producto.is_valid() and form_stock.is_valid():
            stock = form_stock.save(commit=False)
            stock.producto = form_producto.save()
            stock.tienda = request.user.tienda
            stock.save()
            return redirect(self.get_success_url())
        else:
            self.render_to_response(self.get_context_data(form_producto=form_producto, form_stock=form_stock))


# noinspection PyAttributeOutsideInit
class EditarProducto(FormView):
    model = Stock
    template_name = 'producto_form.html'
    form_class = StockForm
    second_form_class = ProductoForm
    success_url = reverse_lazy('tienda:mostrar-tienda')

    def create_fields(self, **kwargs):
        if not hasattr(self, 'stock'):
            stock_id = kwargs['pk']
            self.stock = self.model.objects.get(id=stock_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.create_fields(**self.kwargs)

        context['accion'] = 'Editar'
        context['header'] = 'Edite su Producto'
        context['stock'] = self.stock

        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        self.create_fields(**kwargs)

        form_stock = self.form_class(request.POST, instance=self.stock)
        form_producto = self.second_form_class(request.POST, request.FILES, instance=self.stock.producto)

        if form_stock.is_valid() and form_producto.is_valid():
            imagen = form_producto.cleaned_data.get('imagen', None)
            if imagen:
                form_producto.instance.imagen = imagen

            form_producto.save()
            form_stock.save()
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form_producto=form_producto, form_stock=form_stock))


class EliminarProducto(DeleteView):
    """
    Al eliminar el producto se elimina tambien el stock
    al que pertenece gracias al metodo on_delete=CASCADE
    """
    model = Producto
    template_name = 'producto_eliminar.html'
    success_url = reverse_lazy('tienda:mostrar-tienda')
    context_object_name = 'producto'
