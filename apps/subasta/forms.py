from django import forms

from apps.subasta.models import SubastaEnCurso


class SubastaForm(forms.ModelForm):
    class Meta:
        model = SubastaEnCurso
        fields = ['producto', 'pujante', 'tienda', 'precio_actual', 'hora_final']
