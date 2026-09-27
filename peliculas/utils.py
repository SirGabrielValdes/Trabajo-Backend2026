"""Funciones de apoyo para leer y procesar el archivo peliculas.json."""

import json
from pathlib import Path

RUTA_JSON = Path(__file__).resolve().parent / "data" / "peliculas.json"

# Descripción de la clasificación chilena de películas
CLASIFICACIONES = {
    "TE": "Todo espectador",
    "TE+7": "Todo espectador, inconveniente para menores de 7 años",
    "14": "Mayores de 14 años",
    "18": "Mayores de 18 años",
}


def cargar_peliculas():
    """Lee el archivo JSON y devuelve una lista de diccionarios."""
    try:
        with open(RUTA_JSON, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    for pelicula in datos:
        pelicula["duracion_texto"] = formatear_duracion(pelicula["duracion_min"])
        pelicula["clasificacion_texto"] = CLASIFICACIONES.get(
            pelicula["clasificacion"], "Sin clasificación"
        )
        pelicula["estrellas"] = calcular_estrellas(pelicula["calificacion"])
    return datos


def formatear_duracion(minutos):
    """Convierte 169 en '2 h 49 min'."""
    horas, resto = divmod(minutos, 60)
    if horas == 0:
        return f"{resto} min"
    if resto == 0:
        return f"{horas} h"
    return f"{horas} h {resto} min"


def calcular_estrellas(nota):
    """Transforma una nota de 0 a 10 en un texto de 5 estrellas: '★★★★☆'."""
    llenas = round(nota / 2)
    return "★" * llenas + "☆" * (5 - llenas)


def obtener_generos(peliculas):
    """Devuelve la lista ordenada de géneros sin repetir."""
    generos = set()
    for pelicula in peliculas:
        generos.add(pelicula["genero"])
    return sorted(generos)


def buscar_por_id(peliculas, pelicula_id):
    """Devuelve la película con el id indicado, o None si no existe."""
    for pelicula in peliculas:
        if pelicula["id"] == pelicula_id:
            return pelicula
    return None
