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
        # widgets = {
        #     'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        #     'precio': forms.NumberInput(attrs={'step': '0.05'}),
        #     'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        #     'imagen': forms.ImageField(allow_empty_file=True),
        # }


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'cantidad',
        ]
        # widgets = {
        #     'cantidad': forms.NumberInput()
        # }
