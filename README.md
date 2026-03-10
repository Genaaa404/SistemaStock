# Almacén · Sistema de Control de Stock

App web minimalista en Flask + MySQL para gestión de inventario.

## Estructura del proyecto

```
almacen/
├── app.py                  # Aplicación principal Flask
├── schema.sql              # Base de datos y datos de prueba
├── requirements.txt        # Dependencias Python
└── templates/
    ├── base.html           # Template base (estilos globales)
    ├── public/
    │   └── index.html      # Vista pública del stock
    └── admin/
        ├── base_admin.html # Layout del panel admin (sidebar)
        ├── login.html      # Login administrador
        ├── dashboard.html  # Dashboard con estadísticas
        ├── productos.html  # Lista y gestión de productos
        ├── producto_form.html  # Formulario crear/editar
        └── categorias.html # Gestión de categorías
```

## Instalación

### 1. Crear base de datos MySQL

```bash
mysql -u root -p < schema.sql
```

### 2. Configurar conexión en `app.py`

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tu_password'   # ← cambiar
app.config['MYSQL_DB'] = 'almacen_db'
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> En sistemas Linux puede necesitar: `sudo apt install libmysqlclient-dev`

### 4. Ejecutar

```bash
python app.py
```

La app estará en `http://localhost:5000`

## Credenciales de prueba

| Campo    | Valor     |
|----------|-----------|
| Usuario  | `admin`   |
| Password | `admin123`|

## Rutas

| Ruta                          | Descripción            |
|-------------------------------|------------------------|
| `/`                           | Vista pública del stock |
| `/buscar?q=xxx&categoria=1`   | Búsqueda y filtros     |
| `/admin/login`                | Login administrador    |
| `/admin`                      | Dashboard              |
| `/admin/productos`            | Gestión de productos   |
| `/admin/productos/nuevo`      | Crear producto         |
| `/admin/categorias`           | Gestión de categorías  |

## Funcionalidades

### Panel público
- Grilla de productos con stock en tiempo real
- Búsqueda por nombre, código o descripción
- Filtro por categoría
- Indicador visual de stock (OK / Bajo / Crítico)

### Panel administrador
- Dashboard con estadísticas y alertas
- CRUD completo de productos
- Ajuste rápido de stock (entrada/salida)
- Gestión de categorías
- Acceso protegido por sesión

## Seguridad (para producción)

- Hashear contraseñas con `werkzeug.security`
- Usar variables de entorno para credenciales
- Activar HTTPS
- Cambiar `secret_key` a un valor seguro aleatorio
