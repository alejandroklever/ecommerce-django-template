from django.db import models
from django.contrib.auth.models import User
from apps.tienda.models import Tienda, Producto


class SubastaEnCurso(models.Model):
    pujante = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio_inicial = models.FloatField(default=0.0)
    precio_actual = models.FloatField(null=True)
    hora_inicio = models.DateTimeField()
    hora_final = models.DateTimeField()

    def __str__(self):
        pass


class SubastaFinalizada(models.Model):
    producto = models.CharField(max_length=80)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    precio_final = models.FloatField(null=True)
    hora_final = models.DateTimeField()

    def __str__(self):
        pass
