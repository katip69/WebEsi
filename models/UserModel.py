from flask_login import UserMixin

class User(UserMixin):

    def __init__(self,id,nombre,email,password,admin) -> None:
        self.nombre=nombre
        self.password=password
        self.email=email
        self.id=id
        self.admin=admin


    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT * FROM usuario WHERE id = %s" #esto es una guarrada historica es para probar
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], row[2],None,row[3])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)