# RollSys

Sistema web de gestión para una tienda de patines: inventario, ventas, pedidos a proveedores y cobros, todo en un solo lugar. Proyecto final de Análisis y Desarrollo de Software.

## Qué hace

- **Panel:** ventas del día, dinero por cobrar y productos que toca reponer.
- **Vender:** cada venta descuenta el stock al instante.
- **Inventario:** productos por talla y color, con alerta cuando llegan al stock mínimo.
- **Pedidos:** pedidos a proveedores con seguimiento de estado hasta que llegan.
- **Cobros:** estado de pago de cada venta.

## Tecnologías

Python, Django, SQLite (en desarrollo), HTML y CSS.

## Cómo instalarlo

    git clone git@github.com:jmarulanda1807-pixel/Rollsys.git
    cd Rollsys
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py cargar_ejemplo
    python manage.py runserver

Luego abre http://localhost:8000/ y entra con el usuario que creaste. Los productos se cargan desde http://localhost:8000/admin/ (categorías, proveedores, productos y sus variantes).

## Estructura

- `patines_project/`: configuración de Django.
- `tienda/models.py`: tablas (productos, variantes, ventas, compras, pedidos).
- `tienda/services.py`: reglas de negocio (registrar venta, anular venta, registrar compra).
- `tienda/views.py` y `tienda/urls.py`: las pantallas.
- `tienda/templates/` y `tienda/static/`: diseño y logo.

## Cómo trabajamos

Nadie escribe directo en `main`. Cada tarea va en su propia rama (`feature/nombre-de-la-tarea`) y se une con un Pull Request que revisa otro compañero.

## Equipo

Pendiente: nombres de los integrantes.

## Guía completa de comandos

Todos los comandos del proyecto, paso a paso (instalación, Git y GitHub, ramas y enlace público para compartir), están en [docs/GUIA_COMANDOS.md](docs/GUIA_COMANDOS.md).
