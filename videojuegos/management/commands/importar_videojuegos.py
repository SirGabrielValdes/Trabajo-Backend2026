"""Migra la información de videojuegos.json a la base de datos.

Uso: python manage.py importar_videojuegos
Se puede ejecutar varias veces: no duplica registros.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from videojuegos.models import Desarrolladora, Genero, Plataforma, Videojuego

RUTA_JSON = Path(__file__).resolve().parents[2] / "data" / "videojuegos.json"

PAISES = {
    "Nintendo": "Japón",
    "FromSoftware": "Japón",
    "Mojang Studios": "Suecia",
    "Team Cherry": "Australia",
    "EA Sports": "Estados Unidos",
    "ConcernedApe": "Estados Unidos",
    "Santa Monica Studio": "Estados Unidos",
}

FABRICANTES = {
    "Nintendo Switch": "Nintendo",
    "PS5": "Sony",
    "PS4": "Sony",
    "Xbox Series X|S": "Microsoft",
    "Xbox One": "Microsoft",
    "PC": "Varios",
    "Móvil": "Varios (iOS / Android)",
}


class Command(BaseCommand):
    help = "Importa los videojuegos desde data/videojuegos.json a la base de datos"

    @transaction.atomic
    def handle(self, *args, **options):
        with open(RUTA_JSON, encoding="utf-8") as archivo:
            datos = json.load(archivo)

        for item in datos:
            genero, _ = Genero.objects.get_or_create(nombre=item["genero"])
            desarrolladora, _ = Desarrolladora.objects.get_or_create(
                nombre=item["desarrolladora"],
                defaults={"pais": PAISES.get(item["desarrolladora"], "")},
            )
            juego, creado = Videojuego.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "genero": genero,
                    "desarrolladora": desarrolladora,
                    "anio": item["anio"],
                    "precio": item["precio"],
                    "calificacion": item["calificacion"],
                    "clasificacion": item["clasificacion"],
                    "descripcion": item["descripcion"],
                    "imagen": item["imagen"],
                },
            )
            plataformas = []
            for nombre in item["plataformas"]:
                plataforma, _ = Plataforma.objects.get_or_create(
                    nombre=nombre, defaults={"fabricante": FABRICANTES.get(nombre, "")}
                )
                plataformas.append(plataforma)
            juego.plataformas.set(plataformas)

            estado = "creado" if creado else "actualizado"
            self.stdout.write(f"  {juego.titulo}: {estado}")

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {Videojuego.objects.count()} videojuegos, {Genero.objects.count()} géneros, "
            f"{Desarrolladora.objects.count()} desarrolladoras, {Plataforma.objects.count()} plataformas."
        ))
