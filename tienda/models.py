from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    marca = models.CharField(max_length=80, blank=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos"
    )
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.marca})" if self.marca else self.nombre


class Variante(models.Model):
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="variantes"
    )
    sku = models.CharField(max_length=40, unique=True)
    talla = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=40, blank=True)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=2)
    precio_costo = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ["producto__nombre", "talla", "color"]
        constraints = [
            models.UniqueConstraint(
                fields=["producto", "talla", "color"], name="variante_unica"
            )
        ]

    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo

    def __str__(self):
        return f"{self.producto.nombre} - talla {self.talla} - {self.color}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    documento = models.CharField(max_length=30, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    puntos = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    class Estado(models.TextChoices):
        COMPLETADA = "COMPLETADA", "Completada"
        ANULADA = "ANULADA", "Anulada"

    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventas"
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ventas"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(
        max_length=15, choices=MetodoPago.choices, default=MetodoPago.EFECTIVO
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.COMPLETADA
    )
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha:%Y-%m-%d}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    variante = models.ForeignKey(Variante, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.variante}"


class Compra(models.Model):
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, related_name="compras"
    )
    registrada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="compras"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Compra #{self.pk} - {self.proveedor}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, related_name="detalles"
    )
    variante = models.ForeignKey(Variante, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.costo_unitario