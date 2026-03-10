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
