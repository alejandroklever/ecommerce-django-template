from django.db import models
from django.contrib.auth.models import User
from apps.tienda.models import Tienda, Producto, Stock
from datetime import datetime


class Compra(models.Model):
    fecha_hora = models.DateTimeField(default=datetime.now, blank=True)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ['comprador', 'tienda', 'fecha_hora']

    def __str__(self):
        return f'{self.comprador, self.producto, self.tienda}'


class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    pedidos = models.ManyToManyField('Pedido')


class Pedido(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
