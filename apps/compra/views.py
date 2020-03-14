import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, FormView

from apps.compra.models import Pedido, Compra, Carrito
from apps.tienda.forms import StockForm
from apps.tienda.models import Stock, Tienda


class PagarPedidoVista(FormView):
    pass


# noinspection PyAttributeOutsideInit
class DetalleProductosVista(FormView):
    """
    Clase encargada de mostrar la informacion de un producto de una tienda
    Y mostrar las acciones de comprar o agregar productos al carrito
    """
    model = Pedido
    template_name = 'producto_detalles.html'

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
            return Http404()

    def __handle_pay_action(self, request, context):
        time = datetime.datetime.now()
        comprador = self.request.user
        tienda = context['tienda']
        stock = context['stock']
        cantidad = request.POST['cantidad']

        if stock.cantidad - int(cantidad) < 0:
            # Save code here...
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
        cantidad = request.POST['cantidad']

        try:
            carrito = Carrito.objects.get(usuario_id=user.id)
        except Carrito.DoesNotExist:
            carrito = Carrito(usuario=user)
            carrito.save()

        pedido = Pedido(stock=stock, cantidad=cantidad)
        pedido.save()

        carrito.pedidos.add(pedido)
        return redirect('compra:listar-carrito')


class PagarPedidosDelCarritoVista(FormView):
    pass


class ListarPedidosVista(ListView):
    template_name = 'listar-carrito.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Pedido.objects.filter(carrito__usuario=self.request.user)
