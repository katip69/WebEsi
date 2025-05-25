import random
import logging
from locust import HttpUser, task, between

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/locust.log"),
        logging.StreamHandler()
    ]
)

class TestUser(HttpUser):
    wait_time = between(1, 5)
    def datos_usuario(self):
        return {
            'nombre': f'usuario{random.randint(1, 1000)}',
            'email': f'test{random.randint(1, 1000)}@test',
            'password': '123456',
        }

    # Primera Tarea que se ejecuta al iniciar el usuario
    def on_start(self):
        datos = self.datos_usuario()
        resgistro = self.client.post("/api/registrar", data = datos)
        if resgistro.status_code != 200:
            logging.error("Error al registrar el usuario: %s", datos['nombre'])
        else:
            logging.info("Usario registrado: %s", datos['nombre'])
        inicio = self.client.post("/api/login", data = datos)
        if inicio.status_code != 200:
            logging.error("Error al iniciar sesión: %s", datos['nombre'])
        else:
            logging.info("Usuario logueado: %s", datos['nombre'])

    @task
    def productos(self):
        self.client.get("/api/productos")
        for i in range(1, 3):
            self.client.get(f"/api/productos/{i}")

    @task
    def carrito(self):
        # Obtener un producto aleatorio
        response = self.client.get(f"/api/productos/{random.randint(1, 3)}")
        # TODO: El getProductoPedido(id) deberíaa ser fetchone()??
        if response.status_code == 200:
            producto = response.json()
            
            # Si la respuesta es una lista, accede al primer elemento
            if isinstance(producto, list) and len(producto) > 0:
                producto = producto[0]   
            
            logging.info(f"Producto obtenido: {producto}")
            
            # Usar el producto para agregarlo al carrito
            self.client.post("/api/carrito/agregar", data={
                'id_articulo': producto['id'],
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'cantidad': 1,
                'id_usuario': 1 # TODO: Cambiar por el ID del usuario real
            })
            logging.info("Producto agregado al carrito")
        else:
            logging.error(f"Error al obtener el producto: {response.status_code}")

    @task
    def menu(self):
        self.client.get("/api/menu")
        logging.info("Menú consultado")

    #@task
    #def logout(self):
    #    self.client.get("/api/logout")
    #    logging.info("Usuario deslogueado") 
