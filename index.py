from flask import Flask, jsonify, request
from flask import render_template
from flask_mysqldb import MySQL
import os

app=Flask(__name__)

# Configuración de la base de datos

app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB")


conexion = MySQL(app)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/login")
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
    return render_template('carritoDeCompras.html')


if __name__ == "__main__":
    app.run()
