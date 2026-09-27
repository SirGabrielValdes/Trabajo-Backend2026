from django.http import Http404
from django.shortcuts import render

from .utils import buscar_por_id, cargar_videojuegos, obtener_generos

# Opciones de orden permitidas: valor del parámetro GET -> (campo, descendente)
ORDENES = {
    "titulo": ("titulo", False),
    "precio": ("precio", False),
    "calificacion": ("calificacion", True),
    "anio": ("anio", True),
}


def inicio(request):
    """Página de inicio / presentación del sitio."""
    juegos = cargar_videojuegos()
    total = len(juegos)

    promedio = 0
    if total > 0:
        promedio = round(sum(j["calificacion"] for j in juegos) / total, 1)

    # Los 3 videojuegos mejor calificados
    destacados = sorted(juegos, key=lambda j: j["calificacion"], reverse=True)[:3]

    contexto = {
        "total": total,
        "promedio": promedio,
        "cantidad_generos": len(obtener_generos(juegos)),
        "destacados": destacados,
    }
    return render(request, "videojuegos/inicio.html", contexto)


def listado(request):
    """Catálogo de videojuegos leído desde el archivo JSON, con filtros."""
    juegos = cargar_videojuegos()
    generos = obtener_generos(juegos)

    genero = request.GET.get("genero", "")
    busqueda = request.GET.get("q", "").strip()
    orden = request.GET.get("orden", "titulo")

    if genero:
        juegos = [j for j in juegos if j["genero"] == genero]

    if busqueda:
        texto = busqueda.lower()
        juegos = [
            j for j in juegos
            if texto in j["titulo"].lower() or texto in j["desarrolladora"].lower()
        ]

    if orden not in ORDENES:
        orden = "titulo"
    campo, descendente = ORDENES[orden]
    juegos = sorted(juegos, key=lambda j: j[campo], reverse=descendente)

    contexto = {
        "juegos": juegos,
        "generos": generos,
        "genero_actual": genero,
        "busqueda": busqueda,
        "orden_actual": orden,
    }
    return render(request, "videojuegos/listado.html", contexto)


def detalle(request, juego_id):
    """Ficha de un videojuego y sugerencias que comparten plataforma."""
    juegos = cargar_videojuegos()
    juego = buscar_por_id(juegos, juego_id)
    if juego is None:
        raise Http404("Videojuego no encontrado")

    plataformas = set(juego["plataformas"])
    similares = []
    for otro in juegos:
        if otro["id"] != juego["id"] and plataformas & set(otro["plataformas"]):
            similares.append(otro)
        if len(similares) == 3:
            break

    contexto = {"juego": juego, "similares": similares}
    return render(request, "videojuegos/detalle.html", contexto)
