from django.shortcuts import render
from django.views.generic import ListView, FormView, DetailView

from apps.tienda.models import Tienda, Stock
from .models import Carrito, Pedido


def index(request, pk: int):
    return render(request, 'compra_index.html')


class ListarTiendasVista(ListView):
    """
    Lista de todas las tiendas existentes excepto la del propio usuario
    """
    model = Tienda
    template_name = 'tiendas_listar.html'
    context_object_name = 'tiendas'

    def get_queryset(self):
        return Tienda.objects.exclude(usuario_id=self.request.user.id)


class VisitarTiendaVista(ListView):
    """
    Muestra los productos de la tienda especificada por el parametro pk
    """
    model = Tienda
    template_name = 'tienda_visitar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tienda_id = self.kwargs.get('pk', 0)

        context['tienda'] = Tienda.objects.get(id=tienda_id)
        context['stock_list'] = Stock.objects.filter(tienda_id=tienda_id)

        return context


class PagarProductoVista(FormView):
    pass


class DetalleProductoVista(DetailView):
    """
    Clase encargada de mostrar la informacion de un producto de una tienda
    """
    pass


class ComprarProductoVista(FormView):
    pass


class PagarPedidosDelCarritoVista(FormView):
    pass


class AgregarProductosAlCarritoVista(FormView):
    pass


class ListarPedidosVista(ListView):
    template_name = 'listar-carrito.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Pedido.objects.filter(carrito__usuario=self.request.user)
