import datetime
from utils.db import db

class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable = True)
    cantidad = db.Column(db.Integer,nullable = True)

    producto = db.relationship('Producto', backref = 'ventas')

    def __init__(self,producto_id, cantidad):
        self._producto_id = producto_id
        self._cantidad = cantidad

    
    def to_dict(self):
            return {
                "id_producto": self.producto_id,
                "cantidad": self.cantidad,
            }