from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask import make_response, send_file
import io
# import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app=Flask(__name__, template_folder='Templates') #crea la app

app.secret_key = 'appsecretkey' #clave secreta para la sesion

mysql=MySQL() #inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ventas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app) #inicializa la conexion a la DB


# @app.route('/exportar_excel')
# def exportar_excel():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM productos")
#     productos = cursor.fetchall()
#     cursor.close()

#     # Crear DataFrame
#     df = pd.DataFrame(productos)
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Productos')

#     output.seek(0)
#     return send_file(output,
#                      as_attachment=True,
#                      download_name="productos.xlsx",
#                      mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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
            cursor.execute('SELECT * FROM usuario WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                session['usuario'] = user['email']
                session['rol'] = user['id_rol']
                
                if user['id_rol'] == 1:
                    return render_template("admin.html")
                else:
                    return render_template("inicio.html")
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
        password = request.form.get('password')
        id_rol = 2  # Rol usuario por defecto

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                          (nombre, email, password, id_rol))
            mysql.connection.commit()
            cur.close()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error durante el registro: {e}', 'danger')
            return redirect(url_for('Registro'))

    return render_template ('Registro.html')

@app.route('/Catalogo')
def Catalogo():
  return render_template ('Catalogo.html')

@app.route('/admin')
def admin():
    if 'rol' in session and session['rol'] == 1:
        return render_template("admin.html", usuario=session.get('usuario'))
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
    password = request.form['password']
    sql="UPDATE usuario SET nombre=%s, email=%s, password=%s WHERE id=%s"
    datos=(nombre, email, password, id)
    
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


if __name__ == '__main__':
  app.run(debug=True, port=343)