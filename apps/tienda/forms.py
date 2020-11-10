from django import forms

from .models import Producto, Stock, Tienda


class ActualizarTiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = [
            'nombre',
            'imagen'
        ]


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'precio',
            'descripcion',
            'imagen',
        ]


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'cantidad',
        ]
