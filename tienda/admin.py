from django.contrib import admin

from .models import (
    Categoria,
    Cliente,
    Compra,
    DetalleCompra,
    DetalleVenta,
    Producto,
    Proveedor,
    Variante,
    Venta,
)


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca", "categoria", "precio_venta", "activo")
    list_filter = ("categoria", "marca", "activo")
    search_fields = ("nombre", "marca")
    inlines = [VarianteInline]


@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ("producto", "sku", "talla", "color", "stock", "stock_minimo")
    list_filter = ("producto__categoria",)
    search_fields = ("sku", "producto__nombre")


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "cliente", "vendedor", "metodo_pago", "total", "estado")
    list_filter = ("estado", "metodo_pago", "fecha")
    inlines = [DetalleVentaInline]


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "proveedor", "total")
    inlines = [DetalleCompraInline]


admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Cliente)