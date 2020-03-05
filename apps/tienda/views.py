from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from .forms import ActualizarTiendaForm, ProductoForm, StockForm
from .models import Tienda, Producto, Stock


class ListarTiendas(ListView):
    model = Tienda
    template_name = 'tiendas_listar.html'
    context_object_name = 'tiendas'


class VisitarTienda(ListView):
    model = Tienda
    model2 = Stock
    template_name = 'tienda_visitar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tienda_id = self.kwargs.get('pk', 0)
        tienda = self.model.objects.get(id=tienda_id)
        stock_list = self.model2.objects.filter(tienda=tienda)
        context['tienda'] = tienda
        context['stock_list'] = stock_list

        return context


# noinspection PyAttributeOutsideInit
class MostrarTienda(ListView):
    model = Stock
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

        query = self.model.objects.filter(tienda__usuario_id=self.user.id)
        return query

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.user = self.request.user
        context['nombre_tienda'] = self.user.tienda.nombre
        context['imagen_tienda'] = self.user.tienda.imagen
        return context


# noinspection PyAttributeOutsideInit
class CrearProducto(CreateView):
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
        # LIFE-SAVE LINE
        self.object = self.get_object

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
class EditarProducto(UpdateView):
    model = Stock
    second_model = Producto
    template_name = 'producto_crear_editar.html'
    form_class = StockForm
    second_form_class = ProductoForm
    success_url = reverse_lazy('tienda:mostrar-tienda')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stock_id = self.kwargs.get('pk', 0)
        stock = self.model.objects.get(id=stock_id)
        producto = self.second_model.objects.get(id=stock.producto.id)

        # (SAVE-LINE) Las plantillas no renderizan los campos FloatField
        producto.strprecio = str(producto.precio)
        context['accion'] = 'Editar'
        context['message'] = 'Edite su Producto'
        context['producto'] = producto
        context['stock'] = stock

        return context

    def post(self, request, *args, **kwargs):
        # SAVE-LINE
        self.object = self.get_object

        stock_id = kwargs['pk']
        stock = self.model.objects.get(id=stock_id)
        producto = self.second_model.objects.get(id=stock.producto.id)

        form_stock = self.form_class(request.POST, instance=stock)
        form_producto = self.second_form_class(request.POST, instance=producto)

        if form_stock.is_valid() and form_producto.is_valid():
            form_stock.save()
            form_producto.save()
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
