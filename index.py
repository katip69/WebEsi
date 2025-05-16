from flask import Flask, jsonify, request, redirect, session, url_for
from flask import render_template
from flask_mysqldb import MySQL
from flask_login import LoginManager,login_user,logout_user,login_required
import os
from models.UserModel import User

app=Flask(__name__)

# Configuración de la base de datos

app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB")


conexion = MySQL(app)
app.secret_key = os.getenv("SECRET_KEY", "12345")
login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return User.get_by_id(conexion,id)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/api/login",methods=['GET','POST'])
def auth():
    if request.method=='POST':
        try:
            cursor = conexion.connection.cursor()
            print(request.form["email"])
            email=request.form["email"]
            cursor.execute("SELECT * FROM usuario WHERE email = (%s)", (email,))                        
            auth = cursor.fetchone()
            cursor.close()
            if auth != None:
                user=User(auth[0],auth[1],auth[2],2)
                login_user(user)
                return redirect("/login")
            else:
                return "No existe"
        except Exception as ex:
            return str(ex)
    else:
        return render_template('login.html')
    

@app.route("/login", methods=["GET", "POST"])
def login():
    
        return render_template('login.html')

# Para la vista del usuario

@app.route("/users/<user_id>")
def get_user(user_id):                  # Método que recibe el id del usuario
    user = {
        "id": user_id,
        "name": "test",
        "email": "test@test"}
    query = request.args.get('query')   # Se obtiene el query de la URL
    if query:                           # Si existe el query, se agrega al diccionario
        user['query'] = query
    return jsonify(user), 200           # Se devuelve el usuario en formato JSON

@app.route("/users")
def get_users():
    data={}
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM usuario")
        users = cursor.fetchall()
        data['mensaje'] = 'exito'
    except Exception as ex:
        data['mensaje'] = 'error'
    return jsonify(data), 200

@app.route("/api/registrar", methods=["POST"])
def registrar():
    # Obtener los datos del formulario
    correo = request.form['email']
    password = request.form['password']
    nombre = request.form['nombre']
    session['email'] = correo

    # Insertarlos en la base de datos
    cursor = conexion.connection.cursor()
    cursor.execute("INSERT INTO usuario (nombre,email, password) VALUE (%s,%s, %s)", 
                   (nombre,correo, password))
    conexion.connection.commit()  # ¡No olvides confirmar los cambios!

    return redirect("/login")

@app.route("/productos")
def productos():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM articulo")
        articulos = cursor.fetchall()
        cursor.close()
        return render_template('selectorDeProductos.html', articulos=articulos)
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error al obtener los productos"}), 500

@app.route("/listado")
def listado():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM pedido")
        pedidos = cursor.fetchall()
        cursor.close()
        return render_template('listadoDePedidos.html', pedidos=pedidos)
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error al obtener los pedidos"}), 500

@app.route("/carrito")
def carrito():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM carrito")
        carrito = cursor.fetchall()
        cursor.close()
        return render_template('carritoDeCompras.html', carritos=carrito)
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error al obtener el carrito"}), 500
    
@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    try:
        session['email'] = 'test@test'  # Es una prueba hasta que se pueda iniciar sesión
        # Comprueba que el usuario ha iniciado sesión
        if 'email' not in session:
            return redirect(url_for('login'))
        
        # Recogemos los parámetros necesario para añadirlos a la tabla carrito
        id = request.form.get('id')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        email = session['email']
        
        cursor = conexion.connection.cursor()
        
        # Se comprueba si el artículo ya estaba en el carrito 
        cursor.execute("SELECT cantidad FROM carrito WHERE id_articulo = %s AND id_usuario = %s", (id, email))
        resultado = cursor.fetchone()
        
        # Si es así se actualiza la cantidad que hay, si no se agrega una fila  
        if resultado:
            cantidad = resultado[0]+1
            cursor.execute("UPDATE carrito SET cantidad = %s WHERE id_articulo = %s AND id_usuario = %s", (cantidad, id, email))
        else:
            cursor.execute("SELECT COUNT(*) FROM carrito")
            id_carrito = cursor.fetchone()[0] + 1
            cursor.execute("""
                INSERT INTO carrito (id_carrito, id_articulo, id_usuario, nombre_articulo, precio_articulo, cantidad) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_carrito, id, email, nombre, precio, 1))
        conexion.connection.commit()
        cursor.close()
        return redirect(url_for('productos'))
    except Exception as ex:
        print(f"Error: {str(ex)}")
        return redirect(url_for('productos'))

if __name__ == "__main__":
    app.run(debug=True)
