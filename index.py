import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, redirect,flash, url_for
from flask import render_template,session
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
    return User.get_by_id(conexion,id)

@app.route("/")
@app.route("/index")
def index():
    info = session.get("info")
    if info == None:
        return redirect('/api/menu')
    else:
        return render_template('index.html', info=info)

@app.route("/api/login",methods=['GET','POST'])
def auth():
    if request.method=='POST':
        try:
            cursor = conexion.connection.cursor()
            email=request.form["email"]
            hashPassword = hashlib.sha256(request.form["password"].encode()).hexdigest()
            cursor.execute("SELECT * FROM usuario WHERE email = (%s)", (email,))                        
            auth = cursor.fetchone()
            cursor.close()
            if auth != None:
                user=User(auth[0],auth[1],auth[2],auth[3],auth[4])
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
        return redirect('/login')
    

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template('login.html')

@app.route('/api/logout',methods=["GET","POST"])
def logout():
    logout_user()
    return redirect('/login')

@app.route('/registro')
def registro():
    return render_template('registrar.html')


@app.route("/api/registrar", methods=["POST"])
def registrar():
    # Obtener los datos del formulario
    correo = request.form['email']
    hashPassword = hashlib.sha256(request.form["password"].encode()).hexdigest()
    nombre = request.form['nombre']
    admin = 0

    # Insertarlos en la base de datos
    cursor = conexion.connection.cursor()
    cursor.execute("INSERT INTO usuario (nombre,email, password,admin) VALUE (%s,%s, %s,%s)", 
                   (nombre,correo, hashPassword,admin))
    conexion.connection.commit()  # ¡No olvides confirmar los cambios!

    return redirect("/login")

@app.route("/productos")
def productos():
    articulos=session.get('articulos')
    session.pop('articulos',None)
    if articulos == None:
        return redirect('/api/productos')
    else:
        return render_template('selectorDeProductos.html',articulos=articulos)    


@app.route("/api/productos", methods=["GET"])
def get_productos():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM articulo")
        articulos = cursor.fetchall()
        cursor.close()
        session['articulos']=articulos
        return redirect('/productos')
    except Exception as ex:
        return flash("Error al obtener los productos")


@app.route("/api/productos/<id>", methods=["GET"])
def getProductoPedido(id):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM articulo WHERE id = %s", (id,))
        articulo = cursor.fetchall()
        cursor.close()
        return jsonify(articulo), 200
    except Exception as ex:
        print(ex)
        return jsonify({"error": "Error al obtener el producto"}), 500

@app.route("/api/productos/<id>", methods=["PUT"])
def actualizaProducto(id):
    if current_user.id:
        producto = request.get_json()
        cursor = conexion.connection.cursor()
        try:
            cursor.execute("UPDATE articulo SET nombre = %s, precio_actual = %s, descripcion = %s, cantidad = %s, puntuacion = %s WHERE id = %s",(producto.get("nombre"),producto.get("precio"), producto.get("descripcion"), producto.get("stock"), producto.get("puntuacion"),id,))
            conexion.connection.commit()
            return jsonify("Actualizacion correcta"), 200
        except Exception as ex:
            return jsonify('Error en la actualizacion del `${valor}`'), 500
    else:
        return jsonify("No eres administrador"), 500


@app.route("/api/productos/<int:id>", methods=["PATCH"])
def actualizaElemento(id):
    if current_user.admin==1:
        cursor = conexion.connection.cursor()
        data = request.get_json() 
        cambio = data.get("update")
        valor = data.get("valor")
        try:
            if cambio=='Precio':
                cursor.execute("UPDATE articulo SET precio_actual = %s WHERE id = %s",(valor,id))
                conexion.connection.commit()
                return jsonify("Precio actualizado con exito"),200
            elif cambio == 'Stock':
                cursor.execute("UPDATE articulo SET cantidad = %s WHERE id = %s",(valor,id))
                conexion.connection.commit()
                return jsonify("Precio actualizado con exito"),200
        except Exception as ex:
            return jsonify('Error en la actualizacion del `${valor}`'), 500
    else:
        return jsonify('No eres administrador '), 500

@app.route("/pedidos")
@login_required
def pedidos():
    pedidos=session.get('pedidos')
    session.pop('pedidos',None)
    if pedidos == None:
        return redirect('/api/pedidos')
    else:
        return render_template('listadoDePedidos.html',pedidos=pedidos)    


@app.route("/api/pedidos", methods=["GET"])
@login_required
def listado():
    try:
        id_usuario=current_user.id
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM pedido WHERE id_usuario = %s",(id_usuario,))
        pedidos = cursor.fetchall()
        cursor.close()
        session['pedidos']=pedidos
        return redirect("/pedidos")
    except Exception as ex:
        print(ex)
        return flash("Error al obtener los pedidos")
    
@app.route("/api/pedidos/<id>", methods=["GET"])
def getArticuloPedido(id):
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM detalle_pedido WHERE id_pedido = %s", (id,))
        articulos = cursor.fetchall()
        cursor.close()
        return jsonify (articulos), 200
    except Exception as ex:
        print(ex)
        return flash("Error al obtener el pedido")

@app.route("/carrito")
def carrito():
    carrito = session.get("carrito")
    if carrito == None:
        return redirect('/api/carrito')
    else:
        session.pop('carrito',None)
        print("here",carrito)
        return render_template('carritoDeCompras.html', carritos=carrito)

@app.route("/api/carrito", methods=["GET"])
@login_required
def get_carrito():
    try:
        id_usuario=current_user.id
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT * FROM carrito WHERE id_usuario = %s",(id_usuario,))
        carrito = cursor.fetchall()
        cursor.close()
        if not carrito:
            session["carrito"] = 'vacio'
        else:
            session["carrito"]= carrito 
        return redirect("/carrito")
    except Exception as ex:
        session["carrito"] = 'vacio' 
        return redirect("/carrito")

@app.route("/api/carrito/agregar", methods=["POST"])
@login_required
def agregar_carrito():
    try:        
        # Recogemos los parámetros necesario para añadirlos a la tabla carrito
        id_articulo = int(request.form.get('id'))
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        cantidad = int(request.form.get('cantidad'))
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
        cursor.execute("SELECT cantidad FROM carrito WHERE id_articulo = %s AND id_usuario = %s", (id_articulo, id_usuario))
        resultado = cursor.fetchone()
        
        # Si es así se actualiza la cantidad que hay, si no se agrega una fila  
        if resultado:
            resultado = resultado[0]+1
            cantidad= cantidad-1
            cursor.execute("UPDATE carrito SET cantidad = %s WHERE id_articulo = %s AND id_usuario = %s", (resultado, id_articulo, id_usuario))
            cursor.execute("UPDATE articulo SET cantidad = %s WHERE id=%s", (cantidad, id_articulo))

        else:
            cantidad= cantidad-1
            cursor.execute("""
                INSERT INTO carrito (id_usuario, id_articulo, nombre_articulo, precio_articulo, cantidad) 
                VALUES (%s, %s, %s, %s, %s)
            """, (id_usuario, id_articulo, nombre, precio, 1))
            cursor.execute("UPDATE articulo SET cantidad = %s WHERE id=%s", (cantidad, id_articulo))
        conexion.connection.commit()
        cursor.close()
        flash('Producto agregado al carrito correctamente', 'success')
        return redirect("/productos")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        return flash("Error al agregar al carrito")

@app.route("/api/carrito/vaciar", methods=["DELETE"])
def vaciar_carrito():

    id_usuario=current_user.id
    data = request.get_json(silent=True) or {}
    compra = data.get("compra")
    cursor = conexion.connection.cursor()
    try:
        if compra is True:
            cursor.execute("SELECT id_articulo,cantidad FROM carrito WHERE id_usuario = %s",(id_usuario,))
            articulos=cursor.fetchall()
            for articulo in articulos:
                id_articulo=articulo[0]
                cantidad=articulo[1]
                cursor.execute("UPDATE articulo SET cantidad = cantidad + %s WHERE id = %s", (cantidad, id_articulo))
        cursor.execute("DELETE FROM carrito WHERE id_usuario = %s",(id_usuario,))    
        conexion.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Artículo borrado correctamente"}), 200
    except Exception as ex:
        print(f"Error: {str(ex)}")
        return flash("Error al vaciar el carrito")
    
@app.route("/api/checkout", methods=["POST"])
def procesar_compra():
    try:
        cursor = conexion.connection.cursor()
        # Se obtiene los datos del carrito a partir de su id
        cursor.execute("SELECT * FROM carrito WHERE id_usuario = %s",(current_user.id,))
        carrito = cursor.fetchall()
        
        if carrito:
            fecha_pedido = datetime.now()
            fecha_entrega = fecha_pedido + timedelta(days=3)
            cursor.execute("INSERT INTO pedido (id_usuario, fecha_pedido, fecha_entrega, estado) VALUES (%s, %s, %s,%s)",(current_user.id,fecha_pedido,fecha_entrega,'procesando',))
            conexion.connection.commit()
            cursor.execute("SELECT id FROM pedido WHERE id_usuario = 1 ORDER BY fecha_pedido DESC LIMIT 1;")
            id_pedido=cursor.fetchone()
            for item in carrito:
                cursor.execute("""
                    INSERT INTO  detalle_pedido
                    (id_pedido, id_articulo, nombre_articulo,cantidad)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_pedido,
                    item[1],
                    item[2],
                    item[4]
                ))
            conexion.connection.commit()
            vaciar_carrito()
            time.sleep(3)
            return redirect(url_for('productos'))
        else:
            return flash("Error al obtener el carrito")

    except Exception as ex:
        print(f"Error: {str(ex)}")
        return flash("Error al procesar la compra")
    
@app.route("/api/menu", methods=["GET"])
def menu():
    try:
        cursor = conexion.connection.cursor()
        cursor.execute("SELECT descripcion FROM info")
        info = cursor.fetchone()
        cursor.close()
        if info:
            session["info"] = info[0]  # Guardamos solo si hay descripción
        return redirect(url_for('index'))
    except Exception as ex:
        print(ex)
        flash("Error al obtener el menú")
        return redirect(url_for('index'))
if __name__ == "__main__":
    app.run(debug=True)
