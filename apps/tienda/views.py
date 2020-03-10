from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, FormView

from .forms import ActualizarTiendaForm, ProductoForm, StockForm
from .models import Tienda, Producto, Stock


# noinspection PyAttributeOutsideInit
class MostrarTienda(ListView):
    template_name = 'tienda_usuario_mostrar.html'
    context_object_name = 'user_stock_list'

    def get_queryset(self):
        self.user = self.request.user

        try:
            self.user.tienda
        except ObjectDoesNotExist:
            # Creamos Tienda por Defecto
            self.user.tienda = Tienda(nombre=f'Tienda de {self.user}', usuario=self.user)
            self.user.tienda.save()
        return Stock.objects.filter(tienda__usuario_id=self.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tienda_id'] = self.user.tienda.id
        context['nombre_tienda'] = self.user.tienda
        return context


# noinspection PyAttributeOutsideInit
class EditarTienda(UpdateView):
    model = Tienda
    template_name = 'tienda_usuario_editar.html'
    form_class = ActualizarTiendaForm
    success_url = reverse_lazy('tienda:mostrar-tienda')
    context_object_name = 'tienda'


# noinspection PyAttributeOutsideInit
class CrearProducto(FormView):
    model = Stock
    template_name = 'producto_crear_editar.html'
    form_class = StockForm
    second_form_class = ProductoForm
    success_url = reverse_lazy('tienda:mostrar-tienda')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Crear'
        context['message'] = 'Agregue su producto'
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
    template_name = 'producto_crear_editar.html'
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
        context['message'] = 'Edite su Producto'
        context['stock'] = self.stock

        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        self.create_fields(**kwargs)

        form_stock = self.form_class(request.POST, instance=self.stock)
        form_producto = self.second_form_class(request.POST, instance=self.stock.producto)

        if form_stock.is_valid() and form_producto.is_valid():
            form_producto.save()
            form_stock.save()
            return redirect(self.get_success_url())
        self.render_to_response(self.get_context_data(form_producto=form_producto, form_stock=form_stock))


class EliminarProducto(DeleteView):
    """
    Al eliminar el producto se elimina tambien el stock
    al que pertenece gracias al metodo on_delete=CASCADE
    """
    model = Producto
    template_name = 'producto_eliminar.html'
    success_url = reverse_lazy('tienda:mostrar-tienda')
    context_object_name = 'producto'
