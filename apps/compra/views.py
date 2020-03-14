from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from apps.compra.forms import PedidoForm
from apps.compra.models import Pedido, Compra
from apps.tienda.forms import StockForm
from apps.tienda.models import Stock, Tienda

import datetime


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
    form_class = PedidoForm
    success_url = reverse_lazy('tienda:listar-tiendas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.stock = Stock.objects.get(id=self.kwargs['pk'])
        self.tienda = Tienda.objects.get(id=self.kwargs['tienda_id'])

        context['stock'] = self.stock
        context['tienda'] = self.tienda
        return context

    def post(self, request: WSGIRequest, *args, **kwargs):
        if request.POST['action'] == 'pagar':
            self.__handle_pay_action(request, **kwargs)
        elif request.POST['action'] == 'carrito':
            self.__handle_add_cart_action(request, *args, **kwargs)
        else:
            raise Exception("Invalid POST action")

        return redirect(self.get_success_url())

    def __handle_pay_action(self, request, **kwargs):
        context = self.get_context_data(**kwargs)

        time = datetime.datetime.now()
        comprador = self.request.user
        tienda = context['tienda']
        stock = context['stock']
        cantidad = request.POST['cantidad']

        Compra(fecha_hora=time, tienda=tienda, comprador=comprador, producto=stock.producto, cantidad=cantidad).save()

        form = StockForm({'cantidad': stock.cantidad - int(cantidad)}, instance=stock)
        if form.is_valid():
            form.save()

    def __handle_add_cart_action(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)


class PagarPedidosDelCarritoVista(FormView):
    pass


class AgregarProductosAlCarritoVista(FormView):
    pass


class ListarPedidosVista(ListView):
    template_name = 'listar-carrito.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Pedido.objects.filter(carrito__usuario=self.request.user)
