from flask_login import UserMixin

class User(UserMixin):

    def __init__(self,nombre,email,password) -> None:
        self.nombre=nombre
        self.password=password
        self.email=email
        self.id=2


    @classmethod
    def get_by_id(self, db, id):
        try:
            nombre="Juan"
            cursor = db.connection.cursor()
            print("here")
            sql = "SELECT * FROM usuario WHERE nombre = %s" #esto es una guarrada historica es para probar
            cursor.execute(sql, (nombre,))
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)