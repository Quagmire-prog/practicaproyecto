from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256
import json


app=Flask(__name__, template_folder='Templates') #crea la app

app.secret_key = 'appsecretkey' #clave secreta para la sesion

mysql=MySQL() #inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'bdektgg7gg1apvivnkyb-mysql.services.clever-cloud.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'uke6o5qgonvpilex'
app.config['MYSQL_PASSWORD'] = 'FomMBB9eBL0w6bLQxDrv'
app.config['MYSQL_DB'] = 'bdektgg7gg1apvivnkyb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app) #inicializa la conexion a la DB


@app.route('/exportar_excel')
def exportar_excel():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()

    # Crear DataFrame
    df = pd.DataFrame(productos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')

    output.seek(0)
    return send_file(output,
                     as_attachment=True,
                     download_name="productos.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ✅ Exportar productos a PDF
@app.route('/exportar_pdf')
def exportar_pdf():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()

    # Crear PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 750, "Listado de Productos")

    y = 710
    p.setFont("Helvetica", 10)
    for producto in productos:
        linea = f"ID: {producto['id']} | {producto['nombreproductos']} | Precio: ${producto['precio']} | Stock: {producto['stock']}"
        p.drawString(50, y, linea)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="productos.pdf", mimetype="application/pdf")




@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
            user = cursor.fetchone()
            cursor.close()

            if user and pbkdf2_sha256.verify(password, user['password']):
                # session['logueado'] = True
                # session['id'] = user['id']
                session['usuario'] = user['email']
                session['rol'] = user['id_rol']
                session['nombre'] = user['nombre']
                
                if user['id_rol'] == 1:
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('inicio'))
            else:
                flash('Usuario y contraseña son incorrectos', 'danger')
                return render_template("login.html")
        except Exception as e:
            flash(f'Error al conectar con la base de datos: {e}', 'danger')
            return render_template("login.html")

    return render_template("login.html")

# Rutas de la aplicacion

@app.route('/')
def inicio():
  return render_template ('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('inicio'))

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
  user={'nombre': '','email': ''}
  if request.method == 'GET':
    user['nombre'] = request.args.get('nombre', '')
    user['email'] = request.args.get('email', '')
    user['mensaje'] = request.args.get('mensaje', '')
  return render_template ('contacto.html', usuario=user)

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
  user={'nombre': '','email': '','mensaje': ''}
  if request.method == 'POST':
    user['nombre'] = request.form.get('nombre', '')
    user['email'] = request.form.get('email', '')
    user['mensaje'] = request.form.get('mensaje', '')
  return render_template ('contactopost.html', usuario=user)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/usuario')
def usuario():
    if 'usuario' in session:
        return render_template('usuario.html', usuario=session['usuario'])
    else:
        flash('Debes iniciar sesión para ver esta página.', 'warning')
        return redirect(url_for('login'))

@app.route('/acercade')
def acercade():
    return render_template("acercade.html")

@app.route('/Registro', methods=['GET', 'POST'])
def Registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = pbkdf2_sha256.hash(request.form['password'])
        id_rol = 2  # Rol usuario por defecto

        # Validar que el correo no exista
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('El correo ya está registrado. Por favor inicia sesión.', 'warning')
            cur.close()
            return redirect(url_for('login'))

        try:
            # Insertar usuario
            cur.execute(
                "INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                (nombre, email, password, id_rol)
            )
            mysql.connection.commit()
            cur.close()

            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            cur.close()
            flash(f'Error durante el registro: {e}', 'danger')
            return redirect(url_for('Registro'))

    return render_template('Registro.html')


@app.route('/Catalogo')
def Catalogo():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    return render_template('Catalogo.html', productos=productos)

@app.route('/admin')
def admin():
    if 'rol' in session and session['rol'] == 1:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) as total_productos FROM productos")
        total_productos = cursor.fetchone()['total_productos']
        cursor.execute("SELECT COUNT(*) as total_usuarios FROM usuario")
        total_usuarios = cursor.fetchone()['total_usuarios']
        cursor.close()
        return render_template("admin.html", 
                               usuario=session.get('usuario'), 
                               total_productos=total_productos, 
                               total_usuarios=total_usuarios)
    else:
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('login'))


@app.route('/guardar_usuario', methods=['GET', 'POST'])
def guardar_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        id_rol = 2  # Rol usuario por defecto

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                          (nombre, email, password, id_rol))
            mysql.connection.commit()
            cur.close()
            flash('Usuario guardado exitosamente.', 'success')
            return redirect(url_for('listar'))
        except Exception as e:
            flash(f'Error al guardar el usuario: {e}', 'danger')
            return redirect(url_for('guardar_usuario'))

    return render_template('guardar_usuario.html')

@app.route('/listar_productos_agregados')
def listar_productos_agregados():
    return render_template('AgregarProductos.html')

@app.route('/listar_productos')
def listar_productos():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        cursor.close()
        return render_template("ListaDeProductos.html", productos=productos)

@app.route('/perfil')
def perfil():
    if 'usuario' in session:
        return render_template('perfil.html', usuario=session['usuario'], nombre=session.get('nombre'))
    else:
        flash('Debes iniciar sesión para ver esta página.', 'warning')
        return redirect(url_for('login'))

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para editar tu perfil.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        nuevo_email = request.form.get('email')
        nueva_password = request.form.get('password')

        try:
            conexion = mysql.connection
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE usuario
                SET nombre=%s, email=%s, password=%s
                WHERE email=%s
            """, (nuevo_nombre, nuevo_email, nueva_password, session['usuario']))
            conexion.commit()
            cursor.close()

            session['nombre'] = nuevo_nombre
            session['usuario'] = nuevo_email

            flash('Perfil actualizado correctamente.', 'success')
            return redirect(url_for('perfil'))

        except Exception as e:
            flash(f'Error al actualizar perfil: {e}', 'danger')
            return redirect(url_for('editar_perfil'))

    # GET: mostrar formulario con datos actuales
    return render_template(
        'editar_perfil.html',
        nombre=session.get('nombre'),
        email=session.get('usuario')
    )


@app.route('/perfilAdmin')
def perfilAdmin():
    if 'usuario' in session:
        return render_template('PerfilAdmin.html', usuario=session['usuario'], nombre=session.get('nombre'))
    else:
        flash('Debes iniciar sesión para ver esta página.', 'warning')
        return redirect(url_for('login'))
    

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
      
    if request.method == 'POST':
        nombre = request.form['nombreproductos']
        precio = request.form['precio']
        stock = request.form['stock']
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO productos (nombreproductos, precio, stock) VALUES (%s, %s, %s)",
                           (nombre, precio, stock))
            mysql.connection.commit()
            cursor.close()
            flash('Producto agregado exitosamente.', 'success')
            return redirect(url_for('agregar_producto'))
        except Exception as e:
            flash(f'Error al agregar el producto: {e}', 'danger')
            return redirect(url_for('agregar_producto'))

    return render_template("AgregarProductos.html")

@app.route('/editar_producto/<int:id>', methods=['POST'])
def editar_producto(id):
    # Obtener valores del formulario
    nombre = request.form.get('nombreproductos')
    precio = request.form.get('precio')
    stock = request.form.get('stock')

    try:
        conexion = mysql.connection
        cursor = conexion.cursor()
        sql = """
            UPDATE productos
            SET nombreproductos = %s,
                precio = %s,
                stock = %s
            WHERE id = %s
        """
        datos = (nombre, precio, stock, id)
        cursor.execute(sql, datos)
        conexion.commit()
        cursor.close()
        flash('Producto actualizado correctamente.', 'success')

    except Exception as e:
        flash(f'Error al actualizar el producto: {e}', 'danger')

    return redirect(url_for('listar_productos'))


@app.route('/eliminar_producto/<string:id>')
def eliminar_producto(id):
    flash('Producto eliminado correctamente', 'question')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM productos WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('listar_productos'))



@app.route('/listar')
def listar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")
    usuarios = cur.fetchall()
    cur.close()
    return render_template("usuario.html", usuarios=usuarios)

@app.route('/updateUsuario', methods=['POST'])
def updateUsuario():
    id = request.form['id']
    nombre = request.form['nombre']
    email = request.form['email']
    password = pbkdf2_sha256.hash(request.form['password'])
    id_rol = request.form['rol']
    sql="UPDATE usuario SET nombre=%s, email=%s, password=%s, id_rol=%s WHERE id=%s"
    datos=(nombre, email, password, id_rol, id)

    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    flash('Usuario actualizado correctamente')
    return redirect(url_for('listar'))

@app.route('/borraruser/<string:id>', methods=['GET'])
def borraruser(id):
    flash('Usuario eliminado correctamente', 'question')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuario WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('listar'))

@app.route('/agregar_al_carrito/<int:id_producto>', methods=['POST'])
def agregar_al_carrito(id_producto):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para comprar.', 'warning')
        return redirect(url_for('login'))

    cantidad = int(request.form['cantidad'])
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id_producto,))
    producto = cursor.fetchone()
    cursor.close()

    if producto and cantidad > 0:
        if 'carrito' not in session:
            session['carrito'] = {}
        
        carrito = session['carrito']
        id_producto_str = str(id_producto)

        if id_producto_str in carrito:
            carrito[id_producto_str]['cantidad'] += cantidad
        else:
            carrito[id_producto_str] = {
                'nombre': producto['nombreproductos'],
                'precio': float(producto['precio']),
                'cantidad': cantidad
            }
        
        session['carrito'] = carrito
        flash(f'Se agregaron {cantidad} {producto["nombreproductos"]} al carrito.', 'success')
    else:
        flash('Producto no encontrado o cantidad inválida.', 'danger')

    return redirect(url_for('Catalogo'))

@app.route('/carrito')
def carrito():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver tu carrito.', 'warning')
        return redirect(url_for('login'))

    return render_template('carrito.html')

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    if 'usuario' not in session or 'carrito' not in session or not session['carrito']:
        flash('No hay productos en tu carrito o no has iniciado sesión.', 'warning')
        return redirect(url_for('carrito'))

    try:
        cursor = mysql.connection.cursor()
        
        # Obtener el id del usuario
        cursor.execute("SELECT id FROM usuario WHERE email = %s", (session['usuario'],))
        usuario = cursor.fetchone()
        id_usuario = usuario['id']

        for id_producto_str, item in session['carrito'].items():
            id_producto = int(id_producto_str)
            cantidad = item['cantidad']
            
            # Verificar stock
            cursor.execute("SELECT stock, precio FROM productos WHERE id = %s", (id_producto,))
            producto = cursor.fetchone()
            
            if producto['stock'] >= cantidad:
                nuevo_stock = producto['stock'] - cantidad
                precio_total = producto['precio'] * cantidad

                # Insertar en la tabla de compras
                cursor.execute(
                    "INSERT INTO compras (id_usuario, id_producto, cantidad, precio_total) VALUES (%s, %s, %s, %s)",
                    (id_usuario, id_producto, cantidad, precio_total)
                )

                # Actualizar stock
                cursor.execute(
                    "UPDATE productos SET stock = %s WHERE id = %s",
                    (nuevo_stock, id_producto)
                )
            else:
                flash(f"No hay suficiente stock para {item['nombre']}.", 'danger')
                return redirect(url_for('carrito'))

        mysql.connection.commit()
        cursor.close()

        session.pop('carrito', None)
        return redirect(url_for('gracias'))

    except Exception as e:
        flash(f'Error al procesar la compra: {e}', 'danger')
        return redirect(url_for('carrito'))

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/estadisticas')
def estadisticas():
    if 'rol' not in session or session['rol'] != 1:
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    # Estadísticas de productos
    cursor.execute("SELECT COUNT(*) as total FROM productos")
    total_productos = cursor.fetchone()['total']
    cursor.execute("SELECT SUM(precio * stock) as valor FROM productos")
    valor_inventario = cursor.fetchone()['valor']
    cursor.execute("SELECT * FROM productos ORDER BY stock DESC LIMIT 1")
    producto_mas_stock = cursor.fetchone()

    # Estadísticas de usuarios
    cursor.execute("SELECT COUNT(*) as total FROM usuario")
    total_usuarios = cursor.fetchone()['total']

    # Estadísticas de ventas
    cursor.execute("SELECT COUNT(*) as total FROM compras")
    total_ventas = cursor.fetchone()['total']
    cursor.execute("SELECT SUM(precio_total) as total FROM compras")
    ingresos_totales = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT p.nombreproductos, SUM(c.cantidad) as total_vendido
        FROM compras c
        JOIN productos p ON c.id_producto = p.id
        GROUP BY p.nombreproductos
        ORDER BY total_vendido DESC
        LIMIT 1
    """)
    producto_mas_vendido = cursor.fetchone()

    cursor.execute("""
        SELECT u.nombre, COUNT(c.id) as total_compras
        FROM compras c
        JOIN usuario u ON c.id_usuario = u.id
        GROUP BY u.nombre
        ORDER BY total_compras DESC
        LIMIT 1
    """)
    mejor_cliente = cursor.fetchone()

    # Datos para gráficos
    cursor.execute("""
        SELECT DATE_FORMAT(fecha_compra, '%Y-%m') as mes, SUM(precio_total) as total
        FROM compras
        GROUP BY mes
        ORDER BY mes
    """)
    ventas_mensuales = cursor.fetchall()

    cursor.execute("""
        SELECT p.nombreproductos, SUM(c.cantidad) as total_vendido
        FROM compras c
        JOIN productos p ON c.id_producto = p.id
        GROUP BY p.nombreproductos
        ORDER BY total_vendido DESC
        LIMIT 5
    """)
    top_productos = cursor.fetchall()

    cursor.close()

    # Preparar datos para Chart.js
    labels_ventas = [venta['mes'] for venta in ventas_mensuales]
    datos_ventas = [float(venta['total']) for venta in ventas_mensuales]

    labels_top_productos = [producto['nombreproductos'] for producto in top_productos]
    datos_top_productos = [int(producto['total_vendido']) for producto in top_productos]

    return render_template('estadisticas.html', 
                           total_productos=total_productos,
                           total_usuarios=total_usuarios,
                           valor_inventario=valor_inventario,
                           producto_mas_stock=producto_mas_stock,
                           total_ventas=total_ventas,
                           ingresos_totales=ingresos_totales,
                           producto_mas_vendido=producto_mas_vendido,
                           mejor_cliente=mejor_cliente,
                           labels_ventas=json.dumps(labels_ventas),
                           datos_ventas=json.dumps(datos_ventas),
                           labels_top_productos=json.dumps(labels_top_productos),
                           datos_top_productos=json.dumps(datos_top_productos))


if __name__ == '__main__':
  app.run(debug=True, port=343)