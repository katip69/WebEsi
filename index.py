import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, redirect,flash, url_for
from flask import render_template
from flask_mysqldb import MySQL
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
import os
from models.UserModel import User
import hashlib

app=Flask(__name__)

# Configuración de la base de datos

app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB")


conexion = MySQL(app)
app.secret_key = os.getenv("SECRET_KEY", "DB_PASSWORD")
login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    print("load_user",id)
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
            hashPassword = hashlib.sha256(request.form["password"].encode()).hexdigest()
            print("here",hashPassword)
            cursor.execute("SELECT * FROM usuario WHERE email = (%s)", (email,))                        
            auth = cursor.fetchone()
            cursor.close()
            if auth != None:
                user=User(auth[0],auth[1],auth[2],auth[3])
                if user.password == hashPassword:
                    login_user(user)
                    return redirect("/login")
                else:
                    flash("Invalid password...")
                    return redirect('/login')
            else:
                return "No existe"
        except Exception as ex:
            return str(ex)
    else:
        return render_template('login.html')
    

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template('login.html')

@app.route('/api/logout',methods=["GET","POST"])
def logout():
    logout_user()
    return redirect('/login')

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
    hashPassword = hashlib.sha256(request.form["password"].encode()).hexdigest()
    nombre = request.form['nombre']

    # Insertarlos en la base de datos
    cursor = conexion.connection.cursor()
    cursor.execute("INSERT INTO usuario (nombre,email, password) VALUE (%s,%s, %s)", 
                   (nombre,correo, hashPassword))
    conexion.connection.commit()  # ¡No olvides confirmar los cambios!

    return redirect("/login")

@app.route("/api/productos", methods=["GET"])
def productos():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM articulo")
        articulos = cursor.fetchall()
        cursor.close()
        return render_template('selectorDeProductos.html', articulos=articulos)
    except Exception as ex:
        print(ex)
        return flash("Error al obtener los productos")

@app.route("/api/productos/<id_articulo>", methods=["GET"])
def getProducto(id_articulo):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM articulo WHERE id_articulo = %s", (id_articulo,))
        articulo = cursor.fetchall()
        cursor.close()
        return render_template('selectorDeProductos.html', articulo=articulo)
    except Exception as ex:
        print(ex)
        return flash("Error al obtener el producto")

@app.route("/api/pedidos", methods=["GET"])
def listado():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM pedido")
        pedidos = cursor.fetchall()
        cursor.close()
        return render_template('listadoDePedidos.html', pedidos=pedidos)
    except Exception as ex:
        print(ex)
        return flash("Error al obtener los pedidos")
    
@app.route("/api/pedidos/<id_articulo>", methods=["GET"])
def getArticuloPedido(id_articulo):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM pedido WHERE id_articulo = %s", (id_articulo,))
        articulo = cursor.fetchall()
        cursor.close()
        return render_template('listadoDePedidos.html', articulo=articulo)
    except Exception as ex:
        print(ex)
        return flash("Error al obtener el pedido")

@app.route("/api/carrito", methods=["GET"])
@login_required
def carrito():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM carrito")
        carrito = cursor.fetchall()
        if not carrito:
            return render_template('carritoDeCompras.html', carritos=[])
        cursor.close()
        return render_template('carritoDeCompras.html', carritos=carrito)
    except Exception as ex:
        print(ex)
        return flash("Error al obtener el carrito")

@app.route("/api/carrito/agregar", methods=["POST"])
@login_required
def agregar_carrito():
    try:        
        # Recogemos los parámetros necesario para añadirlos a la tabla carrito
        id_articulo = request.form.get('id')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        usuario = current_user.email
        id_usuario = current_user.id
        
        cursor = conexion.connection.cursor()
        
        cursor.execute("""
            SELECT id, nombre, precio_actual 
            FROM articulo 
            WHERE id = %s AND nombre = %s AND precio_actual = %s
        """, (id_articulo, nombre, precio))
        
        articulo = cursor.fetchone()
        if not articulo:
            flash('El artículo no existe o los datos no coinciden', 'error')
            return redirect(url_for('productos'))

        # Se comprueba si el artículo ya estaba en el carrito 
        cursor.execute("SELECT cantidad FROM carrito WHERE id_articulo = %s AND id_usuario = %s", (id_articulo, usuario))
        resultado = cursor.fetchone()
        
        # Si es así se actualiza la cantidad que hay, si no se agrega una fila  
        if resultado:
            cantidad = resultado[0]+1
            cursor.execute("UPDATE carrito SET cantidad = %s WHERE id_articulo = %s AND id_usuario = %s", (cantidad, id_articulo, usuario))
        else:
            cursor.execute("SELECT COUNT(*) FROM carrito")
            id_carrito = cursor.fetchone()[0] + 1
            cursor.execute("""
                INSERT INTO carrito (id_carrito, id_usuario, id_articulo, nombre_articulo, precio_articulo, cantidad) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_carrito, id_usuario, id_articulo, nombre, precio, 1))
        conexion.connection.commit()
        cursor.close()
        flash('Producto agregado al carrito correctamente', 'success')
        return render_template('selectorDeProductos.html')
    except Exception as ex:
        print(f"Error: {str(ex)}")
        return flash("Error al agregar al carrito")

@app.route("/api/carrito/vaciar", methods=["DELETE"])
def vaciar_carrito():
    try:        
        cursor = conexion.connection.cursor()

        cursor.execute("DELETE FROM carrito")
        cursor.fetchall()
        
        conexion.connection.commit()
        cursor.close()
        return redirect(url_for('productos'))
    except Exception as ex:
        print(f"Error: {str(ex)}")
        return flash("Error al vaciar el carrito")
    
@app.route("/api/checkout", methods=["POST"])
def procesar_compra():
    try:
        cursor = conexion.connection.cursor()
        
        # Se obtiene los datos del carrito a partir de su id
        cursor.execute("SELECT * FROM carrito")
        carrito = cursor.fetchall()
        
        if carrito:
            fecha_pedido = datetime.now()
            fecha_entrega = fecha_pedido + timedelta(days=3)
            for item in carrito:
                cursor.execute("""
                    INSERT INTO pedido 
                    (id_usuario, id_articulo, nombre_articulo, fecha_pedido, fecha_entrega, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    current_user.id,
                    item[2],
                    item[3],
                    fecha_pedido.date(),
                    fecha_entrega.date(),
                    'procesando'
                ))
            vaciar_carrito()
            time.sleep(3)
            return redirect(url_for('productos'))
        else:
            return flash("Error al obtener el carrito")

    except Exception as ex:
        print(f"Error: {str(ex)}")
        return flash("Error al procesar la compra")

if __name__ == "__main__":
    app.run(debug=True)
