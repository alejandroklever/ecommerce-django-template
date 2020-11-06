import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from apps.compra.forms import PedidoForm
from apps.compra.models import Pedido, Compra, Carrito
from apps.tienda.forms import StockForm
from apps.tienda.models import Stock, Tienda, Categoria


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
            # TODO: check for count of items in stock
            pass

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pedidos'] = Pedido.objects.filter(carrito__usuario=self.request.user)
        context['tienda_id'] = self.request.user.tienda.id
        context['categorias'] = Categoria.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        post = [int(p.replace('pedido', '')) for p in request.POST if p.startswith('pedido')]
        pedidos = [Pedido.objects.get(id=x) for x in post]
        for pedido in pedidos:
            self.__pay(pedido)
            self.__del(pedido)
        return redirect(self.get_success_url())

    @staticmethod
    def __pay(pedido):
        fecha = datetime.datetime.now()
        comprador = pedido.usuario
        tienda = pedido.tienda
        stock = pedido.stock
        cantidad = pedido.cantidad

        if stock.cantidad - int(cantidad) < 0:
            # TODO: check for count of items in stock
            pass

        Compra(fecha_hora=fecha, tienda=tienda, comprador=comprador, producto=stock.producto, cantidad=cantidad).save()

        form = StockForm({'cantidad': stock.cantidad - cantidad}, instance=stock)
        if form.is_valid():
            form.save()

    @staticmethod
    def __del(pedido):
        pedido.delete()
