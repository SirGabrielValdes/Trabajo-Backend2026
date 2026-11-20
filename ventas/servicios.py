"""Lógica de la transacción de venta.

Todo ocurre dentro de una transacción de base de datos (transaction.atomic):
si algo falla, por ejemplo falta stock, no se guarda nada.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from videojuegos.models import Videojuego

from .models import DetalleVenta


@transaction.atomic
def registrar_venta(venta_form, detalle_formset, vendedor):
    """Guarda la venta, sus detalles, descuenta el stock y calcula el total."""
    venta = venta_form.save(commit=False)
    venta.vendedor = vendedor
    venta.save()

    total = 0
    for formulario in detalle_formset.forms:
        datos = formulario.cleaned_data
        if not datos:
            continue  # línea vacía

        # select_for_update bloquea el videojuego mientras se descuenta su stock
        juego = Videojuego.objects.select_for_update().get(pk=datos["videojuego"].pk)
        cantidad = datos["cantidad"]
        if cantidad > juego.stock:
            raise ValidationError(f"Stock insuficiente para «{juego.titulo}»: quedan {juego.stock}.")

        subtotal = juego.precio * cantidad
        DetalleVenta.objects.create(
            venta=venta, videojuego=juego, cantidad=cantidad,
            precio_unitario=juego.precio, subtotal=subtotal,
        )
        Videojuego.objects.filter(pk=juego.pk).update(stock=F("stock") - cantidad)
        total += subtotal

    venta.total = total
    venta.save(update_fields=["total"])
    return venta


@transaction.atomic
def anular_venta(venta):
    """Elimina la venta y devuelve al stock las unidades vendidas."""
    for detalle in venta.detalles.all():
        Videojuego.objects.filter(pk=detalle.videojuego_id).update(stock=F("stock") + detalle.cantidad)
    venta.delete()
