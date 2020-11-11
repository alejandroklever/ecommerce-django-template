import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, DeleteView

from apps.compra.forms import PedidoForm, PagoForm
from apps.compra.models import Pedido, Compra, Carrito
from apps.tienda.forms import StockForm
from apps.tienda.models import Stock, Tienda, Categoria


class BankTransactionView(LoginRequiredMixin, FormView):
    form_class = PagoForm
    success_url = reverse_lazy('tienda:listar-productos')

    def get_context_data(self, **kwargs):
        context = super(BankTransactionView, self).get_context_data(**kwargs)
        context['pedido'] = Pedido.objects.get(id=self.kwargs['pk'])
        context['tienda_id'] = self.request.user.tienda.id
        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        password = request.POST['password']
        cuenta = request.POST['numero_de_cuenta']

        if cuenta.isdigit() and len(cuenta) == 16 and request.user.check_password(password):
            if not request.user.tienda.numero_de_cuenta:
                request.user.tienda.numero_de_cuenta = cuenta
                request.user.tienda.save()

            if cuenta == request.user.tienda.numero_de_cuenta:
                return redirect(self.get_success_url())

        context = self.get_context_data(**kwargs)
        context['error_message'] = 'Clave o numero de cuenta incorrecto'
        return self.render_to_response(context)


class EditarPedido(UpdateView):
    model = Pedido
    template_name = 'editar_pedido.html'
    form_class = PedidoForm
    context_object_name = 'pedido'
    success_url = reverse_lazy('compra:listar-carrito')

    def get_context_data(self, **kwargs):
        context = super(EditarPedido, self).get_context_data(**kwargs)
        pedido = Pedido.objects.get(id=self.kwargs['pk'])
        context['tienda_id'] = self.request.user.tienda.id
        context['total'] = pedido.stock.producto.precio * pedido.cantidad
        return context


class EliminarPedido(DeleteView):
    model = Pedido
    template_name = 'eliminar_pedido.html'
    context_object_name = 'pedido'
    success_url = reverse_lazy('compra:listar-carrito')

    def get_context_data(self, **kwargs):
        context = super(EliminarPedido, self).get_context_data(**kwargs)
        context['tienda_id'] = self.request.user.tienda.id
        return context


# noinspection PyAttributeOutsideInit
class DetalleProductosVista(LoginRequiredMixin, FormView):
    """
    Clase encargada de mostrar la informacion de un producto de una tienda
    Y mostrar las acciones de comprar o agregar productos al carrito
    """
    model = Pedido
    template_name = 'producto_detalles.html'
    form_class = PedidoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.stock = Stock.objects.get(id=self.kwargs['pk'])
        self.tienda = Tienda.objects.get(id=self.kwargs['tienda_id'])

        context['stock'] = self.stock
        context['tienda'] = self.tienda

        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.POST['action'] == 'pagar':
            return self.__handle_pay_action(request, context)
        elif request.POST['action'] == 'carrito':
            return self.__handle_add_cart_action(request, context)
        else:
            raise Http404()

    def __handle_pay_action(self, request, context):
        time = datetime.datetime.now()
        comprador = self.request.user
        tienda = context['tienda']
        stock = context['stock']
        cantidad = request.POST['cantidad']

        if stock.cantidad - int(cantidad) < 0:
            context['cantidad'] = int(cantidad)
            context['error_message'] = 'No quedan suficientes productos en la tienda'
            return self.render_to_response(context)

        Compra(fecha_hora=time,
               tienda=tienda,
               comprador=comprador,
               producto=stock.producto,
               cantidad=cantidad).save()

        form = StockForm({'cantidad': stock.cantidad - int(cantidad)}, instance=stock)
        if form.is_valid():
            form.save()

        return redirect('tienda:listar-tiendas')

    def __handle_add_cart_action(self, request, context):
        user = self.request.user
        stock = context['stock']
        tienda = Tienda.objects.get(stock=stock)
        cantidad = int(request.POST['cantidad'])

        carrito, _ = Carrito.objects.get_or_create(usuario_id=user.id)
        pedido, _ = Pedido.objects.get_or_create(defaults={'cantidad': 0, 'tienda': tienda},
                                                 stock_id=stock.id, usuario_id=user.id)

        form = self.form_class({'cantidad': pedido.cantidad + cantidad, 'seleccionado': False}, instance=pedido)

        if form.is_valid():
            form.save()

        carrito.pedidos.add(pedido)
        return redirect('compra:listar-carrito')


class ListarPedidosVista(LoginRequiredMixin, FormView):
    template_name = 'listar_carrito.html'
    form_class = PedidoForm
    success_url = reverse_lazy('compra:listar-carrito')

    order_fields = {
        'nombre': 'stock__producto__nombre',
        'precio': 'stock__producto__nombre',
        'cantidad': 'cantidad',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_dict = self.request.GET
        query_set = Pedido.objects.filter(carrito__usuario=self.request.user)
        if 'search' in query_dict and query_dict['search']:
            query_set = query_set.filter(stock__producto__nombre__contains=query_dict['search'])

        if 'order_by' in query_dict and query_dict['order_by'] in self.order_fields:
            order_key = self.order_fields[query_dict['order_by']]
            if 'sense' in query_dict and query_dict['sense'] == 'descendente':
                order_key = '-' + order_key
            query_set = query_set.order_by(order_key)

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

        for pedido in query_set:
            pedido.total_a_pagar = pedido.cantidad * pedido.stock.producto.precio

        context['page_header_text'] = 'Su Carrito de Compras'
        context['pedidos'] = query_set
        context['tienda_id'] = self.request.user.tienda.id
        context['categorias'] = Categoria.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        post = [int(p.replace('pedido', '')) for p in request.POST if p.startswith('pedido')]
        pedidos = [Pedido.objects.get(id=x) for x in post]
        for pedido in pedidos:
            self.__pay(pedido, **kwargs)
            self.__del(pedido)
        return redirect(self.get_success_url())

    def __pay(self, pedido, **kwargs):
        fecha = datetime.datetime.now()
        comprador = pedido.usuario
        tienda = pedido.tienda
        stock = pedido.stock
        cantidad = pedido.cantidad

        if stock.cantidad - int(cantidad) < 0:
            context = self.get_context_data(**kwargs)
            context['error_message'] = f'Esta pidiendo mas unidades de {stock.producto.nombre} que las que hay ' \
                                       f'en la tienda {tienda.nombre}'
            return self.render_to_response(context)

        Compra(fecha_hora=fecha, tienda=tienda, comprador=comprador, producto=stock.producto, cantidad=cantidad).save()

        form = StockForm({'cantidad': stock.cantidad - cantidad}, instance=stock)
        if form.is_valid():
            form.save()

    @staticmethod
    def __del(pedido):
        pedido.delete()
