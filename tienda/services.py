from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .models import Compra, DetalleCompra, DetalleVenta, Variante, Venta

VALOR_POR_PUNTO = Decimal("10000")


class StockInsuficiente(Exception):
    pass


@transaction.atomic
def registrar_venta(vendedor, items, cliente=None, metodo_pago=Venta.MetodoPago.EFECTIVO):
    if not items:
        raise ValueError("La venta debe tener al menos un producto.")

    venta = Venta.objects.create(
        vendedor=vendedor, cliente=cliente, metodo_pago=metodo_pago
    )
    total = Decimal("0")

    for item in items:
        variante = (
            Variante.objects.select_for_update()
            .select_related("producto")
            .get(pk=item["variante_id"])
        )
        cantidad = item["cantidad"]

        if variante.stock < cantidad:
            raise StockInsuficiente(
                f"Stock insuficiente de {variante}: hay {variante.stock}, se piden {cantidad}."
            )

        detalle = DetalleVenta.objects.create(
            venta=venta,
            variante=variante,
            cantidad=cantidad,
            precio_unitario=variante.producto.precio_venta,
        )
        variante.stock -= cantidad
        variante.save(update_fields=["stock"])
        total += detalle.subtotal

    venta.total = total
    venta.save(update_fields=["total"])

    if cliente:
        cliente.puntos += int(total // VALOR_POR_PUNTO)
        cliente.save(update_fields=["puntos"])

    return venta


@transaction.atomic
def anular_venta(venta):
    if venta.estado == Venta.Estado.ANULADA:
        raise ValueError("La venta ya está anulada.")

    for detalle in venta.detalles.select_related("variante"):
        variante = Variante.objects.select_for_update().get(pk=detalle.variante_id)
        variante.stock += detalle.cantidad
        variante.save(update_fields=["stock"])

    if venta.cliente:
        cliente = venta.cliente
        cliente.puntos = max(0, cliente.puntos - int(venta.total // VALOR_POR_PUNTO))
        cliente.save(update_fields=["puntos"])

    venta.estado = Venta.Estado.ANULADA
    venta.save(update_fields=["estado"])
    return venta


@transaction.atomic
def registrar_compra(proveedor, usuario, items):
    if not items:
        raise ValueError("La compra debe tener al menos un producto.")

    compra = Compra.objects.create(proveedor=proveedor, registrada_por=usuario)
    total = Decimal("0")

    for item in items:
        variante = Variante.objects.select_for_update().get(pk=item["variante_id"])
        detalle = DetalleCompra.objects.create(
            compra=compra,
            variante=variante,
            cantidad=item["cantidad"],
            costo_unitario=Decimal(str(item["costo_unitario"])),
        )
        variante.stock += detalle.cantidad
        variante.precio_costo = detalle.costo_unitario
        variante.save(update_fields=["stock", "precio_costo"])
        total += detalle.subtotal

    compra.total = total
    compra.save(update_fields=["total"])
    return compra


def variantes_con_stock_bajo():
    return Variante.objects.select_related("producto").filter(
        stock__lte=F("stock_minimo"), producto__activo=True
    )