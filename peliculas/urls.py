from django.urls import path

from . import views

app_name = "peliculas"

urlpatterns = [
    path("", views.listado, name="listado"),
    path("<int:pelicula_id>/", views.detalle, name="detalle"),
]
