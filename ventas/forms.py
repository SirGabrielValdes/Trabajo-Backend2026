import re

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from videojuegos.models import Videojuego
from zonaocio.formularios import FormularioBootstrap, validar_unico

from .models import Cliente, DetalleVenta, Venta


def normalizar_rut(valor):
    """Valida un RUT chileno (dígito verificador, módulo 11) y lo deja como 12.345.678-5."""
    limpio = valor.replace(".", "").replace("-", "").replace(" ", "").upper()
    if len(limpio) < 2 or not limpio[:-1].isdigit():
        raise forms.ValidationError("Formato de RUT inválido. Ej: 12.345.678-5")
    cuerpo, digito = limpio[:-1], limpio[-1]

    suma, multiplicador = 0, 2
    for numero in reversed(cuerpo):
        suma += int(numero) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)

    if digito != esperado:
        raise forms.ValidationError("El dígito verificador del RUT no es válido.")
    return f"{int(cuerpo):,}".replace(",", ".") + f"-{digito}"


class ClienteForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["rut", "nombre", "email", "telefono"]

    def clean_rut(self):
        return validar_unico(self, "rut", normalizar_rut(self.cleaned_data["rut"]))

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if telefono and not re.fullmatch(r"\+?[\d ]{8,15}", telefono):
            raise forms.ValidationError("Teléfono inválido. Ej: +56 9 1234 5678")
        return telefono


class VentaForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]


class VideojuegoConStockField(forms.ModelChoiceField):
    """Muestra el precio y el stock disponible de cada videojuego en la lista."""

    def label_from_instance(self, juego):
        return f"{juego.titulo} — {juego.precio_texto} (stock: {juego.stock})"


class DetalleVentaForm(FormularioBootstrap, forms.ModelForm):
    videojuego = VideojuegoConStockField(
        queryset=Videojuego.objects.filter(stock__gt=0).order_by("titulo"), label="Videojuego"
    )

    class Meta:
        model = DetalleVenta
        fields = ["videojuego", "cantidad"]
        widgets = {"cantidad": forms.NumberInput(attrs={"min": 1})}

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad < 1:
            raise forms.ValidationError("La cantidad debe ser al menos 1.")
        return cantidad


class DetalleVentaFormSetBase(BaseInlineFormSet):
    """Validaciones que involucran a todas las líneas de la venta."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        vistos = set()
        for formulario in self.forms:
            datos = formulario.cleaned_data
            if not datos:
                continue
            juego, cantidad = datos["videojuego"], datos["cantidad"]
            if juego.pk in vistos:
                raise forms.ValidationError(
                    f"«{juego.titulo}» está repetido: usa una sola línea y ajusta la cantidad."
                )
            vistos.add(juego.pk)
            if cantidad > juego.stock:
                formulario.add_error("cantidad", f"Stock insuficiente: quedan {juego.stock} unidades.")


DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta, form=DetalleVentaForm, formset=DetalleVentaFormSetBase,
    extra=3, min_num=1, validate_min=True, can_delete=False,
)
