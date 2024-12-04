from utils.db import db


class Ingrediente(db.Model):
    
    __tablename__ = 'ingredientes'
    
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Float)
    calorias = db.Column(db.Float)
    inventario = db.Column(db.Integer)
    es_vegetariano = db.Column(db.Boolean)
    sabor = db.Column(db.String(100))   
    
    def __init__(self, nombre: str, precio: float, calorias: float, inventario: int, es_vegetariano: bool, sabor: str):
        self._nombre = nombre
        self._precio = precio
        self._calorias = calorias
        self._inventario = inventario
        self._es_vegetariano = es_vegetariano
        self._sabor = sabor
        
    def es_sano(self):
        """
        Un ingrediente es sano si tiene menos de 100 calorías y es vegetariano.
        """
        return self.calorias < 100 and self.es_vegetariano
    
    def to_dict(self):
            return {
                "id": self.id,
                "nombre": self.nombre,
                "precio": self.precio,
                "calorias": self.calorias,
                "inventario": self.inventario, 
                "es_vegetariano": self.es_vegetariano,
                "sabor": self.sabor,  
             }
   
   