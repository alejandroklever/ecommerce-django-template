from django.urls import path

from apps.tienda import views

app_name = 'tienda'

urlpatterns = [
    path('',                          views.MostrarTienda.as_view(),    name='mostrar-tienda'),
    path('listar', views.ListaDeTiendas.as_view(), name='listar-tiendas'),
    path('editar/<int:pk>',           views.EditarTienda.as_view(),     name='editar-tienda'),
    path('productos/listar', views.ListaDeProductos.as_view(), name='listar-productos'),
    path('producto/crear',            views.CrearProducto.as_view(),    name='crear-producto'),
    path('producto/editar/<int:pk>',  views.EditarProducto.as_view(),   name='editar-producto'),
    path('producto/delete/<int:pk>',  views.EliminarProducto.as_view(), name='borrar-producto'),
    path('<int:tienda_id>/productos', views.VisitarTienda.as_view(),    name='visitar-tienda'),
]
