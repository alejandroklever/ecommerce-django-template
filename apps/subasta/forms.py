from django import forms

from apps.subasta.models import SubastaEnCurso


class SubastaUpdateForm(forms.ModelForm):
    class Meta:
        model = SubastaEnCurso
        fields = ['pujante', 'precio_actual']


class SubastaCreateForm(forms.ModelForm):
    class Meta:
        model = SubastaEnCurso
        fields = ['producto', 'pujante', 'tienda', 'precio_actual', 'hora_final']
