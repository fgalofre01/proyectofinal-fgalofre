from flask import render_template, redirect, request, url_for,flash,jsonify
from models.Productos import Producto
from models.Ingredientes import Ingrediente
from models.Heladeria import Heladeria
from models.Ventas import Venta
from models.Usuario import Usuario
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from utils.db import db
import datetime
heladeria = Heladeria()

def heladeria_routes(app):

      # Configuración de flask-login
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def cargar_usuario(user_id):
       return Usuario.query.get(int(user_id))

    @app.route("/")
    @login_required
    def index():
        productos = None
        productos = Producto.query.limit(4).all()
        return render_template('index.html', productos = productos or " - ",  usuario = current_user.usuario)
    
    @app.route('/dashboard')
    def dashboard():
        productos = None
        productos = Producto.query.limit(4).all()
        return render_template('dashboard.html', productos = productos or " - ", )
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            usuario = request.form['usuario']
            password = request.form['password']
            usuario = Usuario.query.filter_by(usuario=usuario).first()

            if usuario and password:
                  login_user(usuario)
                  return redirect(url_for('index')) 
            else:   
                flash("Usuario o contraseña incorrectos ", "danger")
                return redirect(url_for('login'))
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Sesión cerrada exitosamente.", "info")
        return redirect(url_for('login'))
    
    @app.route("/mostrar_ingredientes")
    @login_required
    def mostrar_ingredientes():
       if current_user.es_admin or current_user.es_empleado:
            ingredientes = Ingrediente.query.all()
            return render_template('mostrar_ingredientes.html', ingredientes=ingredientes)
       else:
           return render_template('sin_autorizacion.html')
            
    @app.route('/ingredientes_sanos')
    @login_required
    def mostrar_ingrediente_sano():
        if current_user.es_admin or current_user.es_empleado:
            ingredientes = Ingrediente.query.all()  # Obtiene todos los ingredientes
            ingredientes_sanos = []

            # Validar si cada ingrediente es sano
            for ingrediente in ingredientes:
                es_sano = ingrediente.calorias < 100 or ingrediente.es_vegetariano
                ingredientes_sanos.append({
                    "nombre": ingrediente.nombre,
                    "calorias": ingrediente.calorias,
                    "es_sano": es_sano
                })
            return render_template('ingredientes_sanos.html', ingredientes=ingredientes_sanos)
        else:
           return render_template('sin_autorizacion.html')
            
    
    @app.route('/costo_ajustado')
    @login_required
    def mostrar_costo_ajustado():
        if current_user.es_admin or current_user.es_empleado:
            productos = None
            productos = Producto.query.limit(4).all()
            heladeria.productos= []
            for producto in productos:
                costo_total = 0
                for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                    if ingrediente_id:
                        ingrediente = Ingrediente.query.get(ingrediente_id)
                        if ingrediente.nombre:
                            costo_total += ingrediente.precio
                # Agregar los datos del producto con el costo ajustado a la lista
                heladeria.productos.append({
                    'nombre': producto.nombre,
                    'tipo_vaso': producto.tipo_vaso,
                    'costo_ajustado': round(costo_total, 2)
                })

            return render_template('costo_ajustado.html', productos= heladeria.obtener_productos() or " - ")
        else:
            return render_template('sin_autorizacion.html')

    @app.route('/calorias')
    @login_required
    def calcular_calorias():
        if current_user.es_admin or current_user.es_empleado or current_user.es_cliente:
            productos = Producto.query.limit(4).all()
            heladeria.productos= []
            for producto in productos:
                costo_total_calorias = 0
                for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                    if ingrediente_id:
                        ingrediente = Ingrediente.query.get(ingrediente_id)
                        if ingrediente.nombre:
                                costo_total_calorias += ingrediente.calorias * 0.95
                            
                heladeria.productos.append({
                    'nombre': producto.nombre,
                    'tipo_vaso': producto.tipo_vaso,
                    'calorias_totales': round(costo_total_calorias,2)
                })

            return render_template('calorias.html', productos= heladeria.obtener_productos())
        else:
            return render_template('sin_autorizacion.html')
    
    @app.route('/rentabilidad')
    @login_required
    def calcular_rentabilidad():
        if current_user.es_admin:
            productos = Producto.query.limit(4).all()
            heladeria.productos= []
            for producto in productos:
                total_ingredientes = 0
                for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                    if ingrediente_id:
                        ingrediente = Ingrediente.query.get(ingrediente_id)
                        if ingrediente:
                                total_ingredientes += ingrediente.precio
                                costo_rentabilidad = ((producto.precio_publico - total_ingredientes) / total_ingredientes)*100            
                heladeria.productos.append({
                    'nombre': producto.nombre,
                    'tipo_vaso': producto.tipo_vaso,
                    'rentabilidad': round(costo_rentabilidad ,2)
                })

            return render_template('rentabilidad.html', productos= heladeria.obtener_productos())
        else:
            return render_template('sin_autorizacion.html')

    @app.route('/mas_rentable')
    @login_required
    def mas_rentable():
      if current_user.es_admin: 
            productos = Producto.query.limit(4).all()
            producto_rentable = None
            rentabilidad_mayor = float('-inf')
            heladeria.productos= []
            for producto in productos:
                costo_total = 0
                total_ingredientes = 0
                for ingrediente_id in [producto.ingrediente1_id, producto.ingrediente2_id, producto.ingrediente3_id]:
                    if ingrediente_id:
                        ingrediente = Ingrediente.query.get(ingrediente_id)
                        if ingrediente:
                            costo_total += ingrediente.precio
                        if costo_total > 0:
                           rentabilidad = ((producto.precio_publico - costo_total) / costo_total) * 100
                        else:
                            rentabilidad = 0 
                        if rentabilidad > rentabilidad_mayor:
                            rentabilidad_mayor = rentabilidad                                 
                        producto_rentable = {
                            'nombre': producto.nombre,
                            'tipo_vaso': producto.tipo_vaso,
                            'precio': producto.precio_publico,
                            'costo_total': round(costo_total, 2),
                            'rentabilidad': round(rentabilidad, 2)
                        }

            return render_template('mas_rentable.html', producto=producto_rentable)
      else:
          return render_template('sin_autorizacion.html')
    
    @app.route('/registrar_venta', methods=['GET'])
    @login_required
    def mostrar_registro_venta():
        if current_user.es_admin or current_user.es_empleado or current_user.es_cliente:
            productos = Producto.query.limit(4).all()  # Obtiene todos los productos
            return render_template('registrar_venta.html', productos=productos)
        else:
             return render_template('sin_autorizacion.html')
    
    @app.route('/registrar_venta', methods=['POST'])
    @login_required
    def registrar_venta():
        if current_user.es_admin or current_user.es_empleado or current_user.es_cliente:
            if request.method == 'POST':
                producto_id = request.form.get('producto_id', type=int)
                cantidad = request.form.get('cantidad', type=int)
                # Registrar la venta en la base de datos
                producto = Producto.query.get(producto_id)
                if not producto:
                    flash("Producto no encontrado.", "error")
                    return redirect(url_for('mostrar_registro_venta'))
                if producto: 
                    nueva_venta = Venta(producto_id=producto_id, cantidad=cantidad)
                    db.session.add(nueva_venta)
                    producto.ventas_totales = (producto.ventas_totales or 0) + cantidad  
                    db.session.commit()
                    flash(f"¡Venta registrada exitosamente! Vendiste {cantidad} unidad(es) de {producto.nombre}.", "success")
                    
                    return redirect(url_for('mostrar_registro_venta'))
                else:
                    return "Producto no encontrado", 404
        else:
             return render_template('sin_autorizacion.html')
             
    @app.route('/ventas')
    @login_required
    def mostrar_ventas():
        if current_user.es_admin or current_user.es_empleado or current_user.es_cliente:
            ventas = Venta.query.all()
            return render_template('ventas.html', ventas=ventas)
        else:
            return render_template('sin_autorizacion.html')


    @app.route('/ingredientes_categoria')
    @login_required
    def ingredientes_categoria():
        if current_user.es_admin or current_user.es_empleado:
            ingredientes = Ingrediente.query.all()  # Obtiene todos los ingredientes
            ingredientes_clasificados = []

            # Validar cada ingrediente
            for ingrediente in ingredientes:
                if ingrediente.calorias < 100 or ingrediente.es_vegetariano:
                    categoria = "Es sano"
                else:
                    categoria = "No es Sano"

                ingredientes_clasificados.append({
                    "nombre": ingrediente.nombre,
                    "calorias": ingrediente.calorias,
                    "es_vegetariano": ingrediente.es_vegetariano,
                    "categoria": categoria
                })

            return render_template('ingredientes_categoria.html', ingredientes=ingredientes_clasificados)
        else:
            return render_template('sin_autorizacion.html')
    
    @app.route('/producto_mas_vendido')
    @login_required
    def producto_mas_vendido():
        if current_user.es_admin or current_user.es_empleado:
            # Calcular el producto más vendido
            producto = Producto.query.order_by(Producto.ventas_totales.desc()).first()
            
            if producto:
                return render_template('producto_mas_vendido.html', producto=producto)
            else:
                return render_template('producto_mas_vendido.html', producto=None)
        else:
            return render_template('sin_autorizacion.html')
    
    @app.route('/abastecer_inventario', methods=['GET', 'POST'])
    @login_required
    def abastecer_inventario():
        if current_user.es_admin or current_user.es_empleado:  
            if request.method == 'POST':
                ingrediente_id = request.form.get('ingrediente_id')
                heladeria.inventario = int(request.form.get('inventario'))
                
                # Obtener el ingrediente por ID
                ingrediente = Ingrediente.query.get(ingrediente_id)
                if ingrediente:
                    ingrediente.inventario += heladeria.inventario  # Sumar la cantidad al inventario
                    db.session.commit()
                    flash(f'Se abasteció {heladeria.inventario} unidades del ingrediente "{ingrediente.nombre}".', 'success')
                else:
                    flash('Ingrediente no encontrado.', 'error')
                
                return redirect(url_for('abastecer_inventario'))
            
            ingredientes = Ingrediente.query.all()
            return render_template('abastecer_inventario.html', ingredientes=ingredientes)
        else:
            return render_template('sin_autorizacion.html')
        
    @app.route('/renovar_inventario', methods=['GET', 'POST'])
    @login_required
    def renovar_inventario():
        if current_user.es_admin or current_user.es_empleado: 
            if request.method == 'POST':
                    ingrediente_id = request.form.get('ingrediente_id')
                    
                    # Buscar el ingrediente por su ID
                    ingrediente = Ingrediente.query.get(ingrediente_id)
                    if ingrediente:
                        ingrediente.inventario = 0  # Establecer inventario a 0
                        db.session.commit()
                        flash(f'Inventario del ingrediente "{ingrediente.nombre}" renovado a 0.', 'success')
                    else:
                        flash('Ingrediente no encontrado.', 'error')
                    
                    return redirect(url_for('renovar_inventario'))
                
            ingredientes = Ingrediente.query.all()
            return render_template('renovar_inventario.html', ingredientes=ingredientes)
        else:
           return render_template('sin_autorizacion.html')

    @app.route('/vender/<int:producto_id>', methods=['POST'])
    @login_required
    def vender_producto(producto_id):
        if current_user.es_admin or current_user.es_empleado or current_user.es_cliente:
            # Obtener el producto desde la lista de productos (simulación)
            producto = next((p for p in heladeria.productos if p.id == producto_id), None)
            
            if not producto:
                flash("Producto no encontrado.", "error")
                return redirect(url_for('vender_productos'))
            else:
                try:
                    # Intentar vender el producto
                    mensaje = heladeria.vender(producto)
                    flash(mensaje, "success")
                except ValueError as e:
                    # Capturar el error y mostrar el mensaje personalizado
                    flash(f"¡Oh no! Nos hemos quedado sin {str(e)}", "error")

            return redirect(url_for('vender_productos'))
        else:
           return render_template('sin_autorizacion.html')   
        
    @app.route('/registrar_ventas/<int:producto_id>', methods=['POST'])
    @login_required
    def registrar_ventas(producto_id):
        if current_user.es_admin or current_user.es_empleado or current_user.es_cliente:
            # Buscar el producto
            productos = Producto.query.limit(4).all()
            producto = next((p for p in heladeria.productos if p.id == producto_id), None)
            if not producto:
                return render_template('vender_producto.html', productos=heladeria.productos, mensaje="Producto no encontrado.")
            try:
                # Intentar registrar la venta
                mensaje = heladeria.vender(producto)
            except ValueError as e:
                # Capturar error si falta ingrediente
                mensaje = f"¡Oh no! Nos hemos quedado sin {str(e)}."

            # Renderizar el resultado
            return render_template('vender_producto.html', mensaje=mensaje)
        else:
           return render_template('sin_autorizacion.html') 

