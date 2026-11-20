"""Crea los perfiles de usuario (grupos de Django) con sus permisos.

Uso: python manage.py crear_roles
Se puede ejecutar varias veces: actualiza los permisos sin duplicar grupos.

Perfiles:
  - Administrador:  acceso total (todos los mantenedores, ventas y usuarios).
  - Supervisor:     permisos intermedios (crea y modifica en mantenedores, ve
                    todas las ventas y puede anularlas; no elimina registros
                    de mantenedores ni gestiona usuarios).
  - Administrativo: permisos mínimos (consulta el catálogo, gestiona clientes
                    y registra sus propias ventas; sin operaciones críticas).
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from cuentas.roles import ADMINISTRADOR, ADMINISTRATIVO, SUPERVISOR

CATALOGO = [
    "videojuegos.genero", "videojuegos.desarrolladora", "videojuegos.plataforma",
    "videojuegos.videojuego", "peliculas.genero", "peliculas.clasificacion",
    "peliculas.director", "peliculas.pelicula",
]


def permisos(modelos, acciones):
    """Arma códigos de permiso: permisos(["ventas.cliente"], ["view"]) -> ["ventas.view_cliente"]."""
    return [f"{modelo.split('.')[0]}.{accion}_{modelo.split('.')[1]}" for modelo in modelos for accion in acciones]


TODAS = ["add", "change", "delete", "view"]

PERMISOS_POR_ROL = {
    ADMINISTRADOR: (
        permisos(CATALOGO, TODAS)
        + permisos(["ventas.cliente", "ventas.venta", "ventas.detalleventa"], TODAS)
        + ["ventas.ver_todas_las_ventas"]
        + permisos(["auth.user"], TODAS)
        + ["auth.view_group"]
    ),
    SUPERVISOR: (
        permisos(CATALOGO, ["view", "add", "change"])
        + permisos(["ventas.cliente"], ["view", "add", "change"])
        + permisos(["ventas.venta"], ["view", "add", "delete"])
        + permisos(["ventas.detalleventa"], ["view", "add"])
        + ["ventas.ver_todas_las_ventas"]
    ),
    ADMINISTRATIVO: (
        permisos(CATALOGO, ["view"])
        + permisos(["ventas.cliente"], ["view", "add", "change"])
        + permisos(["ventas.venta", "ventas.detalleventa"], ["view", "add"])
    ),
}


class Command(BaseCommand):
    help = "Crea los perfiles Administrador, Supervisor y Administrativo con sus permisos"

    def handle(self, *args, **options):
        for rol, codigos in PERMISOS_POR_ROL.items():
            grupo, creado = Group.objects.get_or_create(name=rol)
            lista = []
            for codigo in codigos:
                app_label, codename = codigo.split(".")
                lista.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))
            grupo.permissions.set(lista)
            estado = "creado" if creado else "actualizado"
            self.stdout.write(f"  {rol}: {estado} con {len(lista)} permisos")
        self.stdout.write(self.style.SUCCESS("Perfiles listos."))
