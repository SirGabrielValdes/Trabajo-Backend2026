from django.urls import path

from . import views

app_name = "ventas"

urlpatterns = [
    # Transacción de venta
    path("", views.listado, name="listado"),
    path("nueva/", views.nueva, name="nueva"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/anular/", views.anular, name="anular"),
    # Mantenedor de clientes
    path("clientes/", views.clientes, name="clientes"),
    path("<slug:entidad>/agregar/", views.agregar, name="agregar"),
    path("<slug:entidad>/<int:pk>/modificar/", views.modificar, name="modificar"),
    path("<slug:entidad>/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
