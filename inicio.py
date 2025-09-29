from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app=Flask(__name__)

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

@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    print("👉 Accediendo a /accesologin")
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        print(f"👉 Datos recibidos - Email: {email}, Password: {password}"  )
        cursor = mysql.connection.cursor()
        print("👉 Ejecutando consulta SQL")
        cursor.execute('SELECT * FROM usuario WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        print("resultado de la query: , ", user)

        if user:
            session['usuario'] = user['email']
            session['rol'] = user['id_rol']
            
            
            # Redirige según el rol del usuario
            if user['id_rol'] == 1:
                print("👉 Redirigiendo a admin")
                return render_template("admin.html") # Página de administrador
            else:
                print("👉 Redirigiendo a inicio")
                return render_template("inicio.html") # Página de inicio
        else:
            flash('Usuario y contraseña son incorrectos', 'danger')
            return render_template("login.html")  # si falla login

    return render_template("login.html")

# Rutas de la aplicacion

@app.route('/')
def inicio():
  return render_template ('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
  user={
    'nombre': '',
    'email': ''
  }
  if request.method == 'GET':
    user['nombre'] = request.args.get('nombre', '')
    user['email'] = request.args.get('email', '')
    user['mensaje'] = request.args.get('mensaje', '')
  return render_template ('contacto.html', usuario=user)

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
  user={
    'nombre': '',
    'email': '',
    'mensaje': ''
  }
  if request.method == 'POST':
    user['nombre'] = request.form.get('nombre', '')
    user['email'] = request.form.get('email', '')
    user['mensaje'] = request.form.get('mensaje', '')
  return render_template ('contactopost.html', usuario=user)

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    usuario={ #Diccionaroio para almacenar los datos del formulario
         'numeroc': '',
         'nombre': '',
         'apellidos': '',
         'direccion': '',
         'mensaje': ''
    }
    if request.method == 'GET':
       usuario['numeroc'] = request.args.get('numeroc')
       usuario['nombre'] = request.args.get('nombre')
       usuario['apellidos'] = request.args.get('apellidos')
       usuario['direccion'] = request.args.get('direccion')
       usuario['mensaje'] = request.args.get('mensaje')
    return render_template('formulario.html', user=usuario)


@app.route('/formulariopost', methods=['GET', 'POST'])
def formulariopost():
    usuario={ #Diccionaroio para almacenar los datos del formulario
         'numeroc': '',
         'nombre': '',
         'apellidos': '',
         'direccion': '',
         'mensaje': ''
    }
    if request.method == 'POST':
       usuario['numeroc'] = request.form.get('numeroc')
       usuario['nombre'] = request.form.get('nombre')
       usuario['apellidos'] = request.form.get('apellidos')
       usuario['direccion'] = request.form.get('direccion')
       usuario['mensaje'] = request.form.get('mensaje')
    return render_template('formulariopost.html', user=usuario)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/usuario')
def usuario():
    return render_template('usuario.html')


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

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                      (nombre, email, password, id_rol))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('inicio'))

    return render_template ('Registro.html')


@app.route('/Catalogo')
def Catalogo():
  return render_template ('Catalogo.html')

@app.route('/admin')
def admin():
    return render_template("admin.html", usuario=session.get('usuario'))


@app.route('/listar_productos_agregados')
def listar_productos_agregados():
    # De momento solo muestra una página vacía
    return render_template("listar_productos_agregados.html")


@app.route('/listar_productos')
def listar_productos():
    # De momento solo muestra una página vacía
    return render_template("listar_productos.html")


@app.route('/listar')
def listar():
    # Ejemplo para mostrar datos del usuario logueado
    return render_template("perfil.html", usuario=session.get('usuario'))



if __name__ == '__main__':
  app.run(debug=True, port=343)#Ejecuta la app en modo depuracion