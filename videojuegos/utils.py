"""Funciones de apoyo para leer y procesar el archivo videojuegos.json."""

import json
from pathlib import Path

RUTA_JSON = Path(__file__).resolve().parent / "data" / "videojuegos.json"


def cargar_videojuegos():
    """Lee el archivo JSON y devuelve una lista de diccionarios.

    Si el archivo no existe o tiene un formato inválido, se devuelve una
    lista vacía para que el sitio no se caiga.
    """
    try:
        with open(RUTA_JSON, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    for juego in datos:
        juego["precio_texto"] = formatear_precio(juego["precio"])
        juego["nivel"], juego["color"] = nivel_calificacion(juego["calificacion"])
    return datos


def formatear_precio(precio):
    """Convierte 59990 en '$59.990' (formato de pesos chilenos)."""
    return "$" + f"{precio:,}".replace(",", ".")


def nivel_calificacion(nota):
    """Devuelve una etiqueta y un color de Bootstrap según la calificación."""
    if nota >= 9.0:
        return "Obra maestra", "success"
    elif nota >= 8.0:
        return "Muy bueno", "primary"
    elif nota >= 7.0:
        return "Bueno", "warning"
    else:
        return "Regular", "secondary"


def obtener_generos(juegos):
    """Cuenta cuántos videojuegos hay por género: {'RPG': 1, ...}."""
    generos = {}
    for juego in juegos:
        genero = juego["genero"]
        generos[genero] = generos.get(genero, 0) + 1
    return dict(sorted(generos.items()))


def buscar_por_id(juegos, juego_id):
    """Recorre la lista y devuelve el videojuego con el id indicado, o None."""
    for juego in juegos:
        if juego["id"] == juego_id:
            return juego
    return None
