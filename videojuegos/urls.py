from django.urls import path

from . import views

app_name = "videojuegos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("videojuegos/", views.listado, name="listado"),
    path("videojuegos/<int:juego_id>/", views.detalle, name="detalle"),
]
