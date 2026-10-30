from decimal import Decimal

from django.core.management.base import BaseCommand

from tienda.models import Categoria, Producto, Proveedor, Variante

# (nombre, marca, categoría, precio, [(sku, talla, color, stock, stock mínimo), ...])
PRODUCTOS = [
    ("Vento Pro", "Vento", "Profesional", 389000, [("VP-38-NG", "38", "Negro", 3, 2), ("VP-40-NG", "40", "Negro", 3, 2)]),
    ("Apex Carbon", "Apex", "Profesional", 520000, [("AC-41-NG", "41", "Negro", 2, 2)]),
    ("Tempo Semi", "Tempo", "Semiprofesional", 249000, [("TS-37-VI", "37", "Violeta", 5, 3), ("TS-39-VI", "39", "Violeta", 4, 3)]),
    ("Flow Junior", "Flow", "Semiprofesional", 219000, [("FJ-33-RS", "33", "Rosa", 3, 4)]),
    ("Cruiser", "Roller", "Recreación", 159000, [("CR-36-RS", "36", "Rosa", 6, 4), ("CR-40-NG", "40", "Negro", 0, 4)]),
    ("Rodamientos ABEC-9", "Speedy", "Accesorios", 38000, [("RO-ABEC9", "", "", 24, 10)]),
    ("Ruedas 80 mm x4", "Speedy", "Accesorios", 62000, [("RU-80", "80 mm", "Violeta", 5, 6)]),
    ("Casco Rider", "Rider", "Accesorios", 79000, [("CA-M-NG", "M", "Negro", 8, 4)]),
    ("Kit de protecciones", "Rider", "Accesorios", 69000, [("KP-M", "M", "Negro", 7, 4)]),
    ("Cordones neón", "Roller", "Accesorios", 12000, [("CN-NE", "", "Neón", 30, 10)]),
]


class Command(BaseCommand):
    help = "Carga productos de ejemplo para probar RollSys (se puede repetir sin duplicar)."

    def handle(self, *args, **options):
        Proveedor.objects.get_or_create(nombre="Andes Skate")
        Proveedor.objects.get_or_create(nombre="Rodar SAS")
        for nombre, marca, cat, precio, variantes in PRODUCTOS:
            categoria, _ = Categoria.objects.get_or_create(nombre=cat)
            producto, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={"marca": marca, "categoria": categoria, "precio_venta": Decimal(precio)},
            )
            for sku, talla, color, stock, minimo in variantes:
                Variante.objects.get_or_create(
                    sku=sku,
                    defaults={"producto": producto, "talla": talla, "color": color,
                              "stock": stock, "stock_minimo": minimo},
                )
        self.stdout.write(self.style.SUCCESS("Productos de ejemplo cargados."))
