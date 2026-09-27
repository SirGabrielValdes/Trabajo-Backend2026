from django.urls import path

from . import views

app_name = "peliculas"

urlpatterns = [
    path("", views.listado, name="listado"),
    path("<int:pelicula_id>/", views.detalle, name="detalle"),
    path("generos/", views.generos, name="generos"),
    path("directores/", views.directores, name="directores"),
    path("clasificaciones/", views.clasificaciones, name="clasificaciones"),
    # Rutas de los botones de acción (marcadores de posición para la Evaluación N°3)
    path("<slug:entidad>/agregar/", views.accion_pendiente,
         {"accion": "agregar"}, name="agregar"),
    path("<slug:entidad>/<int:pk>/modificar/", views.accion_pendiente,
         {"accion": "modificar"}, name="modificar"),
    path("<slug:entidad>/<int:pk>/eliminar/", views.accion_pendiente,
         {"accion": "eliminar"}, name="eliminar"),
]
