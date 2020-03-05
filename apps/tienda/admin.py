from django.contrib import admin
from .models import Producto, Tienda, Stock


# Register your models here.
admin.site.register(Tienda)
admin.site.register(Producto)
admin.site.register(Stock)
