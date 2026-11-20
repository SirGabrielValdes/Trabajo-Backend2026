"""Rutas principales del proyecto ZonaOcio.

Este archivo es el punto de entrada: vincula las rutas definidas en el
urls.py de cada aplicación. Desde la Evaluación N°3 no se usa Django Admin.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("videojuegos.urls")),
    path("peliculas/", include("peliculas.urls")),
    path("cuentas/", include("cuentas.urls")),
    path("ventas/", include("ventas.urls")),
]
