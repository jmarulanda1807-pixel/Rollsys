from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="panel"),
    path("vender/", views.vender, name="vender"),
    path("inventario/", views.inventario, name="inventario"),
    path("pedidos/", views.pedidos, name="pedidos"),
    path("cobros/", views.cobros, name="cobros"),
]
