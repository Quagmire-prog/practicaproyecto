from flask import Flask, render_template
    
app=Flask(__name__)

@app.route('/') # decorador de ruta principal
def home(): # funcion de la ruta principal[]
    return "Hola Mundo"

@app.route('/contacto') # decorador de contacto
def contacto(): # funcion de la ruta de contacto
    return "Esta es la pagina de contacto"

@app.route('/about') #decorador de la ruta acerca de
def about(): # funcion de la ruta acerca de
    return "Esta es la pagina de acerca de"

@app.route('/servicio/<nombre>') # decorador de la ruta servicio
def servicio(nombre): # funcion para la ruta servicio
    return 'El nombre del servicio es: %s' % nombre

@app.route('/edad/<edad>') #decorador de la ruta edad
def edad(edad): #funcion para la ruta edad
    return 'La edad es: {} años'.format(edad)

@app.route('/suma/<int:num1>/<int:num2>') #Ruta de parametros con dos variables
def suma(num1, num2): #funcion para la ruta suma
    resultado=num1 + num2
    return 'La suma de {} y {} es: {}'.format( num1, num2, resultado)

@app.route ('/edadvalor/<int:edad>')#Ruta de parametros con variables entero
def edadvalor(edad):
    if edad < 18:
        return'Eres mayor de edad'
    elif edad >= 18 and edad <65:
        return 'Eres mayor de edad tienes {} años'.format(edad)
    else:
        return 'Eres un adulto mayor, tienes {} años'.format(edad)

if __name__ == '__main__':
  app.run(debug=True, port=3000) #e ejecuta la app en modo depuracion