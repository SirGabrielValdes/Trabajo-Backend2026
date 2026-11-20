from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from zonaocio import crud
from zonaocio.crud import Mantenedor

from .forms import ClienteForm, DetalleVentaFormSet, VentaForm
from .models import Cliente, Venta
from .servicios import anular_venta, registrar_venta


def ventas_visibles(usuario):
    """Administrador y Supervisor ven todas las ventas; el resto solo las propias."""
    ventas = Venta.objects.select_related("cliente", "vendedor")
    if not usuario.has_perm("ventas.ver_todas_las_ventas"):
        ventas = ventas.filter(vendedor=usuario)
    return ventas


# ---------------------------------------------------------------------------
# Mantenedor de clientes
# ---------------------------------------------------------------------------
MANTENEDORES = {
    "clientes": Mantenedor(Cliente, ClienteForm, "ventas:clientes"),
}


@login_required
@permission_required("ventas.view_cliente", raise_exception=True)
def clientes(request):
    """Listado y búsqueda de clientes."""
    busqueda = request.GET.get("q", "").strip()
    registros = Cliente.objects.annotate(total_ventas=Count("ventas")).order_by("nombre")
    if busqueda:
        registros = registros.filter(
            Q(nombre__icontains=busqueda) | Q(rut__icontains=busqueda) | Q(email__icontains=busqueda)
        )
    return render(request, "ventas/clientes.html", {"registros": registros, "busqueda": busqueda})


@login_required
def agregar(request, entidad):
    return crud.crear(request, crud.obtener_mantenedor(MANTENEDORES, entidad))


@login_required
def modificar(request, entidad, pk):
    return crud.modificar(request, crud.obtener_mantenedor(MANTENEDORES, entidad), pk)


@login_required
def eliminar(request, entidad, pk):
    return crud.eliminar(request, crud.obtener_mantenedor(MANTENEDORES, entidad), pk)


# ---------------------------------------------------------------------------
# Transacción: ventas de videojuegos
# ---------------------------------------------------------------------------
@login_required
@permission_required("ventas.view_venta", raise_exception=True)
def listado(request):
    """Listado y búsqueda de ventas (por N°, cliente, RUT o vendedor)."""
    busqueda = request.GET.get("q", "").strip()
    ventas = ventas_visibles(request.user).annotate(unidades=Count("detalles"))
    if busqueda:
        filtro = (
            Q(cliente__nombre__icontains=busqueda) | Q(cliente__rut__icontains=busqueda)
            | Q(vendedor__username__icontains=busqueda)
        )
        if busqueda.isdigit():
            filtro |= Q(pk=int(busqueda))
        ventas = ventas.filter(filtro)
    return render(request, "ventas/listado.html", {"ventas": ventas, "busqueda": busqueda})


@login_required
@permission_required("ventas.view_venta", raise_exception=True)
def detalle(request, pk):
    venta = get_object_or_404(Venta.objects.select_related("cliente", "vendedor"), pk=pk)
    if not ventas_visibles(request.user).filter(pk=venta.pk).exists():
        raise PermissionDenied
    detalles = venta.detalles.select_related("videojuego")
    return render(request, "ventas/detalle.html", {"venta": venta, "detalles": detalles})


@login_required
@permission_required("ventas.add_venta", raise_exception=True)
def nueva(request):
    """Registra una venta: cliente + uno o más videojuegos con su cantidad."""
    venta_form = VentaForm(request.POST or None)
    detalle_formset = DetalleVentaFormSet(request.POST or None, prefix="detalles")

    if request.method == "POST" and venta_form.is_valid() and detalle_formset.is_valid():
        try:
            venta = registrar_venta(venta_form, detalle_formset, request.user)
        except ValidationError as error:
            messages.error(request, error.messages[0])
        else:
            messages.success(request, f"{venta} registrada correctamente. Total: {venta.total_texto}.")
            return redirect("ventas:detalle", pk=venta.pk)

    contexto = {"venta_form": venta_form, "detalle_formset": detalle_formset}
    return render(request, "ventas/formulario.html", contexto)


@login_required
@permission_required("ventas.delete_venta", raise_exception=True)
def anular(request, pk):
    """Anula (elimina) una venta y devuelve el stock. Operación crítica."""
    venta = get_object_or_404(Venta.objects.select_related("cliente"), pk=pk)
    if request.method == "POST":
        nombre = str(venta)
        anular_venta(venta)
        messages.success(request, f"{nombre} anulada. El stock de los videojuegos fue repuesto.")
        return redirect("ventas:listado")
    return render(request, "ventas/anular.html", {"venta": venta})
