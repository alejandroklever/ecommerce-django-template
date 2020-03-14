from django.forms import ModelForm

from apps.compra.models import Pedido


class PedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['cantidad']
