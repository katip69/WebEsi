from flask import Flask
from flask import render_template

app=Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/productos")
def productos():
    return render_template('selectorDeProductos.html')

@app.route("/listado")
def listado():
    return render_template('listadoDePedidos.html')

@app.route("/carrito")
def carrito():
    return render_template('carritoDeCompras.html')


if __name__ == "__main__":
    app.run()
