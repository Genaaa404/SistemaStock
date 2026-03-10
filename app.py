from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from functools import wraps
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'almacen_secret_key_2024'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'almacen_db'
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error DB: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Acceso denegado.', 'error')
            return redirect(url_for('publico'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return redirect(url_for('publico'))

@app.route('/catalogo')
def publico():
    db = get_db()
    productos = []
    categorias = []
    categoria_filter = request.args.get('categoria', '')
    busqueda = request.args.get('q', '')
    if db:
        cur = db.cursor(dictionary=True)
        query = """
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1
        """
        params = []
        if categoria_filter:
            query += " AND c.id = %s"
            params.append(categoria_filter)
        if busqueda:
            query += " AND (p.nombre LIKE %s OR p.descripcion LIKE %s)"
            params.extend([f'%{busqueda}%', f'%{busqueda}%'])
        query += " ORDER BY p.nombre"
        cur.execute(query, params)
        productos = cur.fetchall()
        cur.execute("SELECT * FROM categorias ORDER BY nombre")
        categorias = cur.fetchall()
        db.close()
    return render_template('publico.html', productos=productos, categorias=categorias,
                           categoria_filter=categoria_filter, busqueda=busqueda)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        if db:
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s AND activo = 1",
                        (username, password))
            user = cur.fetchone()
            db.close()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['rol']
                return redirect(url_for('admin_dashboard'))
        flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('publico'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {'total_productos': 0, 'total_stock': 0, 'alertas': 0, 'categorias': 0}
    alertas = []
    movimientos = []

    db = get_db()
    if db:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM productos WHERE activo=1")
        stats['total_productos'] = cur.fetchone()['total']
        cur.close()

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT COALESCE(SUM(stock),0) AS total FROM productos WHERE activo=1")
        stats['total_stock'] = cur.fetchone()['total']
        cur.close()

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM productos WHERE stock <= stock_minimo AND activo=1")
        stats['alertas'] = cur.fetchone()['total']
        cur.close()

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM categorias")
        stats['categorias'] = cur.fetchone()['total']
        cur.close()

        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT p.nombre, p.stock, p.stock_minimo, c.nombre AS categoria
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.stock <= p.stock_minimo AND p.activo = 1
            ORDER BY p.stock ASC LIMIT 5
        """)
        alertas = cur.fetchall()
        cur.close()

        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT m.*, p.nombre AS producto, u.username
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.fecha DESC LIMIT 8
        """)
        movimientos = cur.fetchall()
        cur.close()
        db.close()

    return render_template('admin/dashboard.html', stats=stats, alertas=alertas, movimientos=movimientos)

@app.route('/admin/productos')
@admin_required
def admin_productos():
    db = get_db()
    productos = []
    categorias = []
    if db:
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT p.*, c.nombre AS categoria_nombre
            FROM productos p LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo=1 ORDER BY p.nombre
        """)
        productos = cur.fetchall()
        cur.execute("SELECT * FROM categorias ORDER BY nombre")
        categorias = cur.fetchall()
        db.close()
    return render_template('admin/productos.html', productos=productos, categorias=categorias)

@app.route('/admin/productos/nuevo', methods=['POST'])
@admin_required
def nuevo_producto():
    db = get_db()
    if db:
        cur = db.cursor()
        cur.execute("""
            INSERT INTO productos (nombre, descripcion, categoria_id, stock, stock_minimo, unidad, precio)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (request.form['nombre'], request.form.get('descripcion',''),
              request.form.get('categoria_id') or None, request.form['stock'],
              request.form['stock_minimo'], request.form.get('unidad','unidad'),
              request.form.get('precio', 0)))
        prod_id = cur.lastrowid
        if int(request.form['stock']) > 0:
            cur.execute("""INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id, nota)
                VALUES (%s, 'entrada', %s, %s, 'Stock inicial')""",
                (prod_id, request.form['stock'], session['user_id']))
        db.commit()
        db.close()
        flash('Producto creado correctamente.', 'success')
    return redirect(url_for('admin_productos'))

@app.route('/admin/productos/editar/<int:id>', methods=['POST'])
@admin_required
def editar_producto(id):
    db = get_db()
    if db:
        cur = db.cursor()
        cur.execute("""UPDATE productos SET nombre=%s, descripcion=%s, categoria_id=%s,
            stock_minimo=%s, unidad=%s, precio=%s WHERE id=%s""",
            (request.form['nombre'], request.form.get('descripcion',''),
             request.form.get('categoria_id') or None, request.form['stock_minimo'],
             request.form.get('unidad','unidad'), request.form.get('precio', 0), id))
        db.commit()
        db.close()
        flash('Producto actualizado.', 'success')
    return redirect(url_for('admin_productos'))

@app.route('/admin/productos/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_producto(id):
    db = get_db()
    if db:
        cur = db.cursor()
        cur.execute("UPDATE productos SET activo=0 WHERE id=%s", (id,))
        db.commit()
        db.close()
        flash('Producto eliminado.', 'success')
    return redirect(url_for('admin_productos'))

@app.route('/admin/movimientos')
@admin_required
def admin_movimientos():
    db = get_db()
    movimientos = []
    productos = []
    if db:
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT m.*, p.nombre AS producto, u.username
            FROM movimientos m JOIN productos p ON m.producto_id = p.id
            JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.fecha DESC LIMIT 100
        """)
        movimientos = cur.fetchall()
        cur.execute("SELECT id, nombre FROM productos WHERE activo=1 ORDER BY nombre")
        productos = cur.fetchall()
        db.close()
    return render_template('admin/movimientos.html', movimientos=movimientos, productos=productos)

@app.route('/admin/movimientos/nuevo', methods=['POST'])
@admin_required
def nuevo_movimiento():
    db = get_db()
    if db:
        cur = db.cursor(dictionary=True)
        tipo = request.form['tipo']
        cantidad = int(request.form['cantidad'])
        prod_id = request.form['producto_id']
        cur.execute("SELECT stock FROM productos WHERE id=%s", (prod_id,))
        prod = cur.fetchone()
        if prod:
            nuevo_stock = prod['stock'] + cantidad if tipo == 'entrada' else prod['stock'] - cantidad
            if nuevo_stock < 0:
                flash('Stock insuficiente para realizar la salida.', 'error')
            else:
                cur2 = db.cursor()
                cur2.execute("UPDATE productos SET stock=%s WHERE id=%s", (nuevo_stock, prod_id))
                cur2.execute("""INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id, nota)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (prod_id, tipo, cantidad, session['user_id'], request.form.get('nota','')))
                db.commit()
                flash('Movimiento registrado correctamente.', 'success')
        db.close()
    return redirect(url_for('admin_movimientos'))

@app.route('/admin/categorias')
@admin_required
def admin_categorias():
    db = get_db()
    categorias = []
    if db:
        cur = db.cursor(dictionary=True)
        cur.execute("""SELECT c.*, COUNT(p.id) AS total_productos
            FROM categorias c LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo=1
            GROUP BY c.id ORDER BY c.nombre""")
        categorias = cur.fetchall()
        db.close()
    return render_template('admin/categorias.html', categorias=categorias)

@app.route('/admin/categorias/nueva', methods=['POST'])
@admin_required
def nueva_categoria():
    db = get_db()
    if db:
        cur = db.cursor()
        cur.execute("INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
                    (request.form['nombre'], request.form.get('descripcion','')))
        db.commit()
        db.close()
        flash('Categoría creada.', 'success')
    return redirect(url_for('admin_categorias'))

@app.route('/admin/categorias/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar_categoria(id):
    db = get_db()
    if db:
        cur = db.cursor()
        cur.execute("DELETE FROM categorias WHERE id=%s", (id,))
        db.commit()
        db.close()
        flash('Categoría eliminada.', 'success')
    return redirect(url_for('admin_categorias'))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    db = get_db()
    usuarios = []
    if db:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios ORDER BY username")
        usuarios = cur.fetchall()
        db.close()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/nuevo', methods=['POST'])
@admin_required
def nuevo_usuario():
    db = get_db()
    if db:
        cur = db.cursor()
        cur.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s,%s,%s,%s)",
                    (request.form['username'], request.form['password'],
                     request.form.get('nombre',''), request.form.get('rol','empleado')))
        db.commit()
        db.close()
        flash('Usuario creado.', 'success')
    return redirect(url_for('admin_usuarios'))

if __name__ == '__main__':
    app.run(debug=True)
