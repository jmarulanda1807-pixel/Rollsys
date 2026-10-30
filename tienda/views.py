from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from . import services
from .models import Categoria, Pedido, Proveedor, Variante, Venta

OK = Venta.Estado.COMPLETADA


def base(vista, **extra):
    return {
        "vista": vista,
        "n_bajo": services.variantes_con_stock_bajo().count(),
        "n_ped": Pedido.objects.filter(estado__lt=3).count(),
        "n_cobrar": Venta.objects.filter(pagada=False, estado=OK).count(),
        **extra,
    }


def suma(qs):
    return qs.aggregate(t=Sum("total"))["t"] or 0


@login_required
def panel(request):
    hoy = timezone.localdate()
    dias = ["L", "M", "X", "J", "V", "S", "D"]
    barras = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        barras.append({"dia": dias[d.weekday()], "t": suma(Venta.objects.filter(fecha__date=d, estado=OK))})
    mx = max([b["t"] for b in barras] + [1])
    for b in barras:
        b["alto"] = max(round(b["t"] / mx * 72), 6)
    return render(request, "tienda/panel.html", base(
        "panel",
        total_hoy=suma(Venta.objects.filter(fecha__date=hoy, estado=OK)),
        por_cobrar=suma(Venta.objects.filter(pagada=False, estado=OK)),
        reponer=services.variantes_con_stock_bajo(),
        ultimas=Venta.objects.all()[:4],
        barras=barras,
    ))


@login_required
def vender(request):
    if request.method == "POST":
        items = []
        for v in Variante.objects.all():
            n = request.POST.get(f"q_{v.id}", "0")
            if n.isdigit() and int(n) > 0:
                items.append({"variante_id": v.id, "cantidad": int(n)})
        try:
            venta = services.registrar_venta(
                request.user, items,
                metodo_pago=request.POST.get("metodo", "EFECTIVO"),
                pagada=request.POST.get("pagada") == "1",
            )
            messages.success(request, f"Venta #{venta.id} registrada. El inventario ya se descontó.")
        except (services.StockInsuficiente, ValueError) as e:
            messages.error(request, str(e))
        return redirect("vender")
    q, cat = request.GET.get("q", ""), request.GET.get("cat", "")
    vs = Variante.objects.select_related("producto__categoria").filter(producto__activo=True)
    if q:
        vs = vs.filter(producto__nombre__icontains=q)
    if cat:
        vs = vs.filter(producto__categoria__nombre=cat)
    return render(request, "tienda/vender.html", base(
        "vender", variantes=vs, q=q, cat=cat, categorias=Categoria.objects.all()))


@login_required
def inventario(request):
    if request.method == "POST":
        Variante.objects.filter(pk=request.POST.get("id")).update(stock=F("stock") + 5)
        messages.success(request, "Ingreso de 5 unidades registrado.")
        return redirect("inventario")
    vs = Variante.objects.select_related("producto__categoria")
    return render(request, "tienda/inventario.html", base("inventario", variantes=vs))


@login_required
def pedidos(request):
    if request.method == "POST":
        if request.POST.get("accion") == "crear":
            v = get_object_or_404(Variante, pk=request.POST.get("id"))
            if Pedido.objects.filter(variante=v, estado__lt=3).exists():
                messages.error(request, f"Ya hay un pedido en camino de {v.producto.nombre}.")
            else:
                Pedido.objects.create(
                    variante=v, proveedor=Proveedor.objects.first(),
                    cantidad=max(v.stock_minimo * 2 - v.stock, v.stock_minimo))
                messages.success(request, "Pedido creado.")
        else:
            with transaction.atomic():
                p = get_object_or_404(Pedido.objects.select_for_update(), pk=request.POST.get("id"))
                if p.estado < 3:
                    p.estado += 1
                    p.save(update_fields=["estado"])
                    if p.estado == 3:
                        Variante.objects.filter(pk=p.variante_id).update(stock=F("stock") + p.cantidad)
                        messages.success(request, f"Recibido: +{p.cantidad} al inventario.")
        return redirect("pedidos")
    return render(request, "tienda/pedidos.html", base(
        "pedidos", pedidos=Pedido.objects.select_related("variante__producto", "proveedor")))


@login_required
def cobros(request):
    if request.method == "POST":
        Venta.objects.filter(pk=request.POST.get("id")).update(pagada=True)
        messages.success(request, "Cobro marcado como pagado.")
        return redirect("cobros")
    return render(request, "tienda/cobros.html", base("cobros", ventas=Venta.objects.filter(estado=OK)))
