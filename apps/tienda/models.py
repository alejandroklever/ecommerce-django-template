from django.db import models
from django.contrib.auth.models import User


class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion = models.TextField(null=True)
    imagen = models.ImageField(upload_to='producto', default='default_product_image.jpg', null=True, blank=True)
    categoria = models.OneToOneField('Categoria', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.nombre} : {self.precio}'


class Tienda(models.Model):
    nombre = models.CharField(max_length=80)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    inventario = models.ManyToManyField(Producto, through='Stock')
    imagen = models.ImageField(upload_to='tienda', default='default_tienda_image.jpg', null=True, blank=True)
    correo = models.EmailField(max_length=200, default='noemail@gmail.com')
    numero_de_cuenta = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return f'{self.nombre}'


class Stock(models.Model):
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['producto', 'tienda']

    def __str__(self):
        return f'{self.cantidad} unidades de {self.producto} en la tienda {self.tienda}'


class Categoria(models.Model):
    tag = models.CharField(default='Otros', max_length=25, unique=True)

    def __str__(self):
        return self.tag
