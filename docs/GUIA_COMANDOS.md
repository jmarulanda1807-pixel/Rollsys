# Guía de comandos de RollSys

Todos los comandos que usamos para armar el proyecto, en orden. Se ejecutan en la terminal de Linux (Penguin del Chromebook). Cada bloque se copia y se pega tal cual.

## 1. Instalar herramientas

    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip git unzip wget
    python3 --version
    git --version

## 2. Crear el proyecto Django

    mkdir ~/tienda-patines
    cd ~/tienda-patines
    python3 -m venv venv
    source venv/bin/activate
    pip install django
    django-admin startproject patines_project .
    python manage.py startapp tienda
    pip freeze > requirements.txt
    code .

El punto al final de `startproject` es importante. Cuando el entorno está activo, la línea de la terminal empieza con `(venv)`.

## 3. Configurar el proyecto

En `patines_project/settings.py`: agregar `"tienda"` a `INSTALLED_APPS`, cambiar `LANGUAGE_CODE = "es"` y `TIME_ZONE = "America/Bogota"` (el nombre de la zona, no `UTC-5`), y al final del archivo:

    LOGIN_URL = "login"
    LOGIN_REDIRECT_URL = "panel"
    LOGOUT_REDIRECT_URL = "login"

En `patines_project/urls.py`:

    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("accounts/", include("django.contrib.auth.urls")),
        path("", include("tienda.urls")),
    ]

## 4. Base de datos y arranque

    python manage.py makemigrations tienda
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Abrir http://localhost:8000/ y entrar con el usuario creado. Para detener el servidor: `Ctrl + C`.

## 5. Datos de ejemplo

    python manage.py cargar_ejemplo

Se puede repetir sin duplicar productos.

## 6. Git y GitHub (primera vez)

    printf 'venv/\n__pycache__/\n*.pyc\ndb.sqlite3\n.env\n.vscode/\n' > .gitignore
    git init -b main
    git config --global user.name "Tu Nombre"
    git config --global user.email "tu-correo@ejemplo.com"
    ssh-keygen -t ed25519 -C "tu-correo@ejemplo.com"
    cat ~/.ssh/id_ed25519.pub

Copiar la línea que muestra el último comando y pegarla en GitHub, en github.com/settings/keys, con **New SSH key**. Luego:

    ssh -T git@github.com
    git add .
    git commit -m "Proyecto base"
    git remote add origin git@github.com:jmarulanda1807-pixel/Rollsys.git
    git push -u origin main

## 7. Guardar cambios (todos los días)

    git status
    git add .
    git commit -m "Describe lo que hiciste"
    git push

Antes de empezar a trabajar: `git pull`.

## 8. Cómo se suma cada compañero

Primero debe aceptar la invitación al repositorio. Después:

    git clone git@github.com:jmarulanda1807-pixel/Rollsys.git
    cd Rollsys
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py cargar_ejemplo
    python manage.py runserver

Cada quien tiene su propia base de datos (`db.sqlite3` no se comparte).

## 9. Trabajo en ramas

    git checkout main
    git pull
    git checkout -b feature/nombre-de-la-tarea
    git add .
    git commit -m "Describe lo que hiciste"
    git push -u origin feature/nombre-de-la-tarea

Luego se abre un Pull Request en GitHub para que otro compañero lo revise.

## 10. Enlace público temporal

Instalar cloudflared (una sola vez):

    wget -O /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo apt install -y /tmp/cloudflared.deb

En `settings.py` deben estar estas dos líneas:

    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".trycloudflare.com"]
    CSRF_TRUSTED_ORIGINS = ["https://*.trycloudflare.com"]

Crear un usuario para los invitados y ponerle contraseña (no usar la del administrador):

    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('amigos')"
    python manage.py changepassword amigos

Encender, en dos pestañas de la terminal (con el `+` de arriba):

    python manage.py runserver
    cloudflared tunnel --url http://localhost:8000

El enlace `https://....trycloudflare.com` cambia cada vez. Funciona solo mientras las dos pestañas estén abiertas y el computador esté despierto.

## 11. Problemas comunes

- **No aparece `(venv)`:** `cd ~/tienda-patines` y luego `source venv/bin/activate`.
- **La terminal no deja escribir:** el servidor está corriendo; `Ctrl + C`.
- **`Incorrect timezone setting`:** usar `America/Bogota`, no `UTC-5`.
- **`dpkg was interrupted`:** `sudo dpkg --configure -a` y repetir la instalación.
- **`Key is invalid` en GitHub:** copiar la clave con `code ~/.ssh/id_ed25519.pub`, `Ctrl + A`, `Ctrl + C`.

## 12. Encender RollSys con un solo comando

Crear el script (una sola vez):

```bash
cat > ~/iniciar-rollsys.sh << 'EOF'
#!/bin/bash
cd ~/tienda-patines
source venv/bin/activate
(sleep 4 && xdg-open http://localhost:8000/ >/dev/null 2>&1) &
python manage.py runserver
EOF
chmod +x ~/iniciar-rollsys.sh
```

Para encender el sistema cada vez:

```bash
~/iniciar-rollsys.sh
```

Entra a la carpeta, activa el entorno, enciende el servidor y abre el navegador. Para apagarlo: `Ctrl + C`.

## 13. El facturador (HTML)

Es una página independiente, sin Django ni base de datos, hecha con HTML, CSS y JavaScript en un solo archivo. Sirve para emitir comprobantes de venta con número consecutivo, imprimirlos o guardarlos en PDF y ver el historial.

Estructura dentro del repositorio:

- `index.html`: portada con el logo y un botón que abre el facturador.
- `facturador/index.html`: el facturador.

El logo se toma de `tienda/static/tienda/logo.png`, por eso la ruta en el facturador es `../tienda/static/tienda/logo.png`.

Mover el facturador a su carpeta (ya hecho):

```bash
mkdir facturador
git mv facturador.html facturador/index.html
sed -i 's#src="tienda/static/tienda/logo.png"#src="../tienda/static/tienda/logo.png"#' facturador/index.html
sed -i 's#href="facturador.html"#href="facturador/"#' index.html
```

Para modificarlo: `code facturador/index.html`, guardar con `Ctrl + S` y luego `git add .`, `git commit -m "Describe el cambio"` y `git push`.

Cosas que se configuran dentro del facturador, en la pestaña Ajustes: nombre de la tienda, NIT, dirección, teléfono, prefijo de numeración, próximo número, IVA y el texto al pie. El IVA queda en 0 %: debe confirmarse con el contador de la tienda.

Notas importantes:

- Los comprobantes se guardan solo en el navegador de cada persona. No pasan a otro computador ni a la base de datos de Django.
- Es un comprobante de venta. No reemplaza la factura electrónica de la DIAN.

## 14. Publicar con GitHub Pages

1. El repositorio debe ser público (Settings, sección Danger Zone, Change repository visibility).
2. En Settings, entrar a Pages (`github.com/jmarulanda1807-pixel/Rollsys/settings/pages`).
3. En Source dejar Deploy from a branch, elegir la rama `main` y la carpeta `/ (root)`, y presionar Save.
4. Esperar de 1 a 2 minutos y abrir los enlaces:

```
https://jmarulanda1807-pixel.github.io/Rollsys/
https://jmarulanda1807-pixel.github.io/Rollsys/facturador/
```

Si sale un 404, esperar un minuto y recargar con `Ctrl + Shift + R`. Cada vez que se haga `git push`, la página se actualiza sola.
