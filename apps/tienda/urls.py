from django.urls import path

from apps.tienda.views import (MostrarTienda, EditarTienda, CrearProducto, EditarProducto, EliminarProducto,
                               ListarTiendas, VisitarTienda, ListarProductos)

app_name = 'tienda'

urlpatterns = [
    path('',                          MostrarTienda.as_view(),    name='mostrar-tienda'),
    path('listar',                    ListarTiendas.as_view(),    name='listar-tiendas'),
    path('editar/<int:pk>',           EditarTienda.as_view(),     name='editar-tienda'),
    path('productos/listar',          ListarProductos.as_view(),  name='listar-productos'),
    path('producto/crear',            CrearProducto.as_view(),    name='crear-producto'),
    path('producto/editar/<int:pk>',  EditarProducto.as_view(),   name='editar-producto'),
    path('producto/delete/<int:pk>',  EliminarProducto.as_view(), name='borrar-producto'),
    path('<int:tienda_id>/productos', VisitarTienda.as_view(),    name='visitar-tienda'),

]
