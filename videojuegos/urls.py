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
    # Mantenedores (CRUD): <entidad> es la clave del diccionario MANTENEDORES
    path("videojuegos/<slug:entidad>/agregar/", views.agregar, name="agregar"),
    path("videojuegos/<slug:entidad>/<int:pk>/modificar/", views.modificar, name="modificar"),
    path("videojuegos/<slug:entidad>/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
