"""Rutas principales del proyecto ZonaOcio.

Este archivo es el punto de entrada: vincula las rutas definidas en el
urls.py de cada aplicación.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("videojuegos.urls")),
    path("peliculas/", include("peliculas.urls")),
]
