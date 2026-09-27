from django.urls import path

from . import views

app_name = "videojuegos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("videojuegos/", views.listado, name="listado"),
    path("videojuegos/<int:juego_id>/", views.detalle, name="detalle"),
    path("videojuegos/generos/", views.generos, name="generos"),
    path("videojuegos/desarrolladoras/", views.desarrolladoras, name="desarrolladoras"),
    path("videojuegos/plataformas/", views.plataformas, name="plataformas"),
    # Rutas de los botones de acción (marcadores de posición para la Evaluación N°3)
    path("videojuegos/<slug:entidad>/agregar/", views.accion_pendiente,
         {"accion": "agregar"}, name="agregar"),
    path("videojuegos/<slug:entidad>/<int:pk>/modificar/", views.accion_pendiente,
         {"accion": "modificar"}, name="modificar"),
    path("videojuegos/<slug:entidad>/<int:pk>/eliminar/", views.accion_pendiente,
         {"accion": "eliminar"}, name="eliminar"),
]
