from flask import jsonify
from models.Productos import Producto
from models.Ingredientes import Ingrediente
from models.Ventas import Venta
from flask_restful import Resource, reqparse
from utils.db import db
import datetime

def heladeria_apis(api):  

    parser = reqparse.RequestParser()
    parser.add_argument('inventario', type=int, help="Inventario debe ser un número")


    class ProductosResource(Resource):
        def get(self):
            productos = Producto.query.limit(4).all()
            return jsonify([producto.to_dict() for producto in productos])

    api.add_resource(ProductosResource, '/api/productos')


    class ProductoByIDResource(Resource):
        def get(self, producto_id):
            producto = Producto.query.get(producto_id)
            if producto:
                return jsonify(producto.to_dict())
            return {"message": "Producto no encontrado"}, 404

    api.add_resource(ProductoByIDResource, '/api/productos/<int:producto_id>')


    class ProductoByNombreResource(Resource):
        def get(self, nombre):
            producto = Producto.query.filter_by(nombre=nombre).first()
            if producto:
                return jsonify(producto.to_dict())
            return {"message": "Producto no encontrado"}, 404

    api.add_resource(ProductoByNombreResource, '/api/productos/nombre/<string:nombre>')


    class CaloriasProductoResource(Resource):
        def get(self, producto_id):
            producto = Producto.query.get(producto_id)
            costo_total_calorias = 0
            if producto:
                for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                    if ingrediente_id:
                        ingrediente = Ingrediente.query.get(ingrediente_id)
                        if ingrediente.nombre:
                                costo_total_calorias += ingrediente.calorias * 0.95
                
                return {
                        "id": producto.id,
                        "nombre": producto.nombre,
                        "total_calorias": round(costo_total_calorias,2),
                    }
            return {"message": "Producto no encontrado"}, 404
    api.add_resource(CaloriasProductoResource, '/api/productos/<int:producto_id>/calorias')


    class RentabilidadProductoResource(Resource):
        def get(self, producto_id):
            producto = Producto.query.get(producto_id)
            total_ingredientes = 0
            if producto:
                    for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                        if ingrediente_id:
                            ingrediente = Ingrediente.query.get(ingrediente_id)
                            if ingrediente:
                                    total_ingredientes += ingrediente.precio
                                    costo_rentabilidad = ((producto.precio_publico - total_ingredientes) / total_ingredientes)*100 
                    return {
                        "id": producto.id,
                        "nombre": producto.nombre,
                        "rentabilidad": round(costo_rentabilidad ,2)
                        }
            return {"message": "Producto no encontrado"}, 404

    api.add_resource(RentabilidadProductoResource, '/api/productos/<int:producto_id>/rentabilidad')

    class CostoProduccionResource(Resource):
        def get(self, producto_id):
            producto = Producto.query.get(producto_id)
            costo_total = 0
            if producto:
                for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                    if ingrediente_id:
                        ingrediente = Ingrediente.query.get(ingrediente_id)
                        if ingrediente.nombre:
                            costo_total += ingrediente.precio
                return {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "costo_produccion": round(costo_total,2)
                    }
            return {"message": "Producto no encontrado"}, 404

    api.add_resource(CostoProduccionResource, '/api/productos/<int:producto_id>/costo')

    class VenderProductoResource(Resource):
        def post(self):
            parser = reqparse.RequestParser()
            parser.add_argument('producto_id', type=int, required=True, help="El ID del producto es obligatorio.")
            parser.add_argument('cantidad', type=int, required=True, help="La cantidad es obligatoria.")
            args = parser.parse_args()

            producto = Producto.query.get(args['producto_id'])
            if not producto:
                return {"message": "Producto no encontrado"}, 404

            if producto:
                  nueva_venta = Venta(producto_id=producto.id, cantidad= args['cantidad'])
                  db.session.add(nueva_venta)
                  db.session.commit()
                  # Actualizar las ventas totales del producto (opcional)
                  producto.ventas_totales = (producto.ventas_totales or 0) + args['cantidad']
                  db.session.commit()
            # Aquí se podría verificar el inventario si estuviera implementado
                  return {
                      "message": "¡Vendido!", "producto": producto.to_dict(),
                       "id": producto.id,
                       "nombre": producto.nombre,
                       "registro_venta": nueva_venta.to_dict(),
                      }
            
    api.add_resource(VenderProductoResource, '/api/productos//ventas/registrar')


    class IngredientesResource(Resource):
        def get(self):
            ingredientes = Ingrediente.query.all()
            return [ingrediente.to_dict() for ingrediente in ingredientes], 200
        
    api.add_resource(IngredientesResource, '/api/ingredientes')

    
    class IngredienteByIDResource(Resource):
        def get(self, ingrediente_id):
            ingrediente = Ingrediente.query.get(ingrediente_id)
            if ingrediente:
                return ingrediente.to_dict(), 200
            return {"message": "Ingrediente no encontrado"}, 404
        
    api.add_resource(IngredienteByIDResource, '/api/ingredientes/<int:ingrediente_id>')
        
    class IngredienteByNombreResource(Resource):
        def get(self, nombre):
            ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
            if ingrediente:
                return ingrediente.to_dict(), 200
            return {"message": "Ingrediente no encontrado"}, 404
        
    api.add_resource(IngredienteByNombreResource, '/api/ingredientes/nombre/<string:nombre>')
        
    class IngredienteEsSanoResource(Resource):
        def get(self, ingrediente_id):
            ingrediente = Ingrediente.query.get(ingrediente_id)
            if ingrediente:
                es_sano = ingrediente.calorias < 100 or ingrediente.es_vegetariano
                return {
                     "nombre": ingrediente.nombre,
                     "calorias": ingrediente.calorias,
                     "es_sano": es_sano,
                       }, 200
            return {"message": "Ingrediente no encontrado"}, 404
        
    api.add_resource(IngredienteEsSanoResource, '/api/ingredientes/es_sano/<int:ingrediente_id>')
        
    class ReabastecerIngredienteResource(Resource):
        def post(self, ingrediente_id):
            args = parser.parse_args()
            inventario = args.get("inventario", 0)
            ingrediente = Ingrediente.query.get(ingrediente_id)
            if ingrediente:
                ingrediente.inventario += inventario
                db.session.commit()
                return {"message": f"Ingrediente {ingrediente.nombre} reabastecido a {ingrediente.inventario}"}, 200
            return {"message": "Ingrediente no encontrado"}, 404
        
    api.add_resource(ReabastecerIngredienteResource, '/api/ingredientes/<int:ingrediente_id>/reabastecer')
           
    class RenovarIngredienteResource(Resource):
        def post(self, ingrediente_id):
            ingrediente = Ingrediente.query.get(ingrediente_id)
            if ingrediente:
                ingrediente.inventario = 0
                db.session.commit()
                return {"message": f"Inventario del ingrediente {ingrediente.nombre} renovado a 0"}, 200
            return {"message": "Ingrediente no encontrado"}, 404
        
    api.add_resource(RenovarIngredienteResource, '/api/ingredientes/<int:ingrediente_id>/renovar')   

    







