from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Usuario, Producto, Pedido, DetallePedido

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    productos_destacados = Producto.query.limit(4).all()
    return render_template('index.html', productos=productos_destacados)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return redirect(url_for('main.index'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado')
            return redirect(url_for('main.registro'))
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=generate_password_hash(password)
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        login_user(nuevo_usuario)
        return redirect(url_for('main.index'))
    return render_template('registro.html')

@main.route('/productos')
def productos():
    productos = Producto.query.all()
    return render_template('selectorDeProductos.html', productos=productos)

@main.route('/carrito')
@login_required
def carrito():
    if 'carrito' not in session:
        session['carrito'] = []
    
    productos_carrito = []
    total = 0
    for item in session['carrito']:
        producto = Producto.query.get(item['producto_id'])
        if producto:
            subtotal = producto.precio * item['cantidad']
            productos_carrito.append({
                'producto': producto,
                'cantidad': item['cantidad'],
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('carritoDeCompras.html', 
                         productos=productos_carrito, 
                         total=total)

@main.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
@login_required
def agregar_al_carrito(producto_id):
    if 'carrito' not in session:
        session['carrito'] = []
    
    cantidad = int(request.form.get('cantidad', 1))
    
    # Verificar si el producto ya está en el carrito
    for item in session['carrito']:
        if item['producto_id'] == producto_id:
            item['cantidad'] += cantidad
            session.modified = True
            return redirect(url_for('main.carrito'))
    
    session['carrito'].append({
        'producto_id': producto_id,
        'cantidad': cantidad
    })
    session.modified = True
    return redirect(url_for('main.carrito'))

@main.route('/finalizar_compra', methods=['POST'])
@login_required
def finalizar_compra():
    if 'carrito' not in session or not session['carrito']:
        flash('El carrito está vacío')
        return redirect(url_for('main.carrito'))
    
    nuevo_pedido = Pedido(usuario_id=current_user.id)
    db.session.add(nuevo_pedido)
    
    for item in session['carrito']:
        producto = Producto.query.get(item['producto_id'])
        if producto and producto.stock >= item['cantidad']:
            detalle = DetallePedido(
                pedido_id=nuevo_pedido.id,
                producto_id=producto.id,
                cantidad=item['cantidad'],
                precio_unitario=producto.precio
            )
            producto.stock -= item['cantidad']
            db.session.add(detalle)
        else:
            flash(f'Stock insuficiente para {producto.nombre}')
            return redirect(url_for('main.carrito'))
    
    try:
        db.session.commit()
        session['carrito'] = []
        flash('Compra realizada con éxito')
        return redirect(url_for('main.listado'))
    except Exception as e:
        db.session.rollback()
        flash('Error al procesar la compra')
        return redirect(url_for('main.carrito'))

@main.route('/listado')
@login_required
def listado():
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).order_by(Pedido.fecha.desc()).all()
    return render_template('listadoDePedidos.html', pedidos=pedidos)