"""Migra la información de peliculas.json a la base de datos.

Uso: python manage.py importar_peliculas
Se puede ejecutar varias veces: no duplica registros.
"""

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from peliculas.models import Clasificacion, Director, Genero, Pelicula

RUTA_JSON = Path(__file__).resolve().parents[2] / "data" / "peliculas.json"

CLASIFICACIONES = {
    "TE": "Todo espectador",
    "TE+7": "Todo espectador, inconveniente para menores de 7 años",
    "14": "Mayores de 14 años",
    "18": "Mayores de 18 años",
}

NACIONALIDADES = {
    "Christopher Nolan": "Reino Unido",
    "Joaquim Dos Santos": "Estados Unidos",
    "Kemp Powers": "Estados Unidos",
    "Justin K. Thompson": "Estados Unidos",
    "Denis Villeneuve": "Canadá",
    "Kelsey Mann": "Estados Unidos",
    "James Wan": "Australia",
    "Bong Joon-ho": "Corea del Sur",
    "Lee Unkrich": "Estados Unidos",
}


class Command(BaseCommand):
    help = "Importa las películas desde data/peliculas.json a la base de datos"

    @transaction.atomic
    def handle(self, *args, **options):
        with open(RUTA_JSON, encoding="utf-8") as archivo:
            datos = json.load(archivo)

        # Se crean todas las clasificaciones, aunque alguna no tenga películas
        for codigo, descripcion in CLASIFICACIONES.items():
            Clasificacion.objects.get_or_create(codigo=codigo, defaults={"descripcion": descripcion})

        for item in datos:
            genero, _ = Genero.objects.get_or_create(nombre=item["genero"])
            clasificacion = Clasificacion.objects.get(codigo=item["clasificacion"])
            pelicula, creado = Pelicula.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "genero": genero,
                    "clasificacion": clasificacion,
                    "anio": item["anio"],
                    "duracion_min": item["duracion_min"],
                    "calificacion": item["calificacion"],
                    "sinopsis": item["sinopsis"],
                    "imagen": item["imagen"],
                },
            )
            # "A, B y C" -> ["A", "B", "C"]
            directores = []
            for nombre in re.split(r",\s*|\s+y\s+", item["director"]):
                director, _ = Director.objects.get_or_create(
                    nombre=nombre, defaults={"nacionalidad": NACIONALIDADES.get(nombre, "")}
                )
                directores.append(director)
            pelicula.directores.set(directores)

            estado = "creada" if creado else "actualizada"
            self.stdout.write(f"  {pelicula.titulo}: {estado}")

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {Pelicula.objects.count()} películas, {Genero.objects.count()} géneros, "
            f"{Director.objects.count()} directores, {Clasificacion.objects.count()} clasificaciones."
        ))
