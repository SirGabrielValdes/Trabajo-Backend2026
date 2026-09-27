from django.http import Http404
from django.shortcuts import render

from .utils import buscar_por_id, cargar_peliculas, obtener_generos


def listado(request):
    """Cartelera de películas leída desde el archivo JSON.

    Permite filtrar por género, buscar por título/director y cambiar entre
    vista de tarjetas o de tabla.
    """
    peliculas = cargar_peliculas()
    generos = obtener_generos(peliculas)

    genero = request.GET.get("genero", "")
    busqueda = request.GET.get("q", "").strip()
    vista = request.GET.get("vista", "tarjetas")

    if genero:
        peliculas = [p for p in peliculas if p["genero"] == genero]

    if busqueda:
        texto = busqueda.lower()
        peliculas = [
            p for p in peliculas
            if texto in p["titulo"].lower() or texto in p["director"].lower()
        ]

    if vista != "tabla":
        vista = "tarjetas"

    # Ordenadas de la más reciente a la más antigua
    peliculas = sorted(peliculas, key=lambda p: p["anio"], reverse=True)

    duracion_total = 0
    for pelicula in peliculas:
        duracion_total += pelicula["duracion_min"]

    contexto = {
        "peliculas": peliculas,
        "generos": generos,
        "genero_actual": genero,
        "busqueda": busqueda,
        "vista": vista,
        "horas_totales": round(duracion_total / 60, 1),
    }
    return render(request, "peliculas/listado.html", contexto)


def detalle(request, pelicula_id):
    """Ficha de una película y otras películas del mismo director o género."""
    peliculas = cargar_peliculas()
    pelicula = buscar_por_id(peliculas, pelicula_id)
    if pelicula is None:
        raise Http404("Película no encontrada")

    relacionadas = [
        p for p in peliculas
        if p["id"] != pelicula["id"]
        and (p["director"] == pelicula["director"] or p["genero"] == pelicula["genero"])
    ]

    contexto = {"pelicula": pelicula, "relacionadas": relacionadas}
    return render(request, "peliculas/detalle.html", contexto)
