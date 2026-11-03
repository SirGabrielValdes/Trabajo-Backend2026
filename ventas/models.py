from django.conf import settings
from django.db import models

from videojuegos.models import Videojuego


class Cliente(models.Model):
    """Persona que compra videojuegos en la tienda."""

    rut = models.CharField("RUT", max_length=12, unique=True, help_text="Ej: 12.345.678-5")
    nombre = models.CharField("nombre completo", max_length=120)
    email = models.EmailField("correo electrónico", blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Venta(models.Model):
    """Transacción: venta de uno o más videojuegos a un cliente."""

    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="ventas", verbose_name="cliente"
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ventas",
        verbose_name="vendedor",
    )
    fecha = models.DateTimeField("fecha", auto_now_add=True)
    total = models.PositiveIntegerField("total (CLP)", default=0)

    class Meta:
        verbose_name = "venta"
        verbose_name_plural = "ventas"
        ordering = ["-fecha"]
        permissions = [("ver_todas_las_ventas", "Puede ver las ventas de todos los vendedores")]

    def __str__(self):
        return f"Venta N°{self.pk}"

    @property
    def total_texto(self):
        return "$" + f"{self.total:,}".replace(",", ".")


class DetalleVenta(models.Model):
    """Cada videojuego vendido dentro de una venta (relación Venta - Videojuego)."""

    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name="detalles", verbose_name="venta"
    )
    videojuego = models.ForeignKey(
        Videojuego, on_delete=models.PROTECT, related_name="detalles_venta",
        verbose_name="videojuego",
    )
    cantidad = models.PositiveIntegerField("cantidad")
    precio_unitario = models.PositiveIntegerField("precio unitario (CLP)")
    subtotal = models.PositiveIntegerField("subtotal (CLP)")

    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"
        constraints = [
            models.UniqueConstraint(fields=["venta", "videojuego"], name="videojuego_unico_por_venta"),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.videojuego}"

    @property
    def precio_texto(self):
        return "$" + f"{self.precio_unitario:,}".replace(",", ".")

    @property
    def subtotal_texto(self):
        return "$" + f"{self.subtotal:,}".replace(",", ".")
