from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Configuración básica de Swagger
app.config['SWAGGER'] = {
    'title': 'Carrito de Compras API',
    'uiversion': 3
}
swagger = Swagger(app)

# Configuración Base de Datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'carrito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelos de Base de Datos (SQLAlchemy) ---

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicio = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"id": self.id, "servicio": self.servicio, "precio": self.precio}

class CartItem(db.Model):
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    
    # Relación para acceder a los datos del servicio fácilmente
    service = db.relationship('Service')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="COMPLETED")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

    service = db.relationship('Service')


# --- Inicialización de Base de Datos ---
def init_db():
    with app.app_context():
        db.create_all()
        # Sembrar catálogo si está vacío
        if Service.query.count() == 0:
            initial_services = [
                {"servicio": "Cambio de Pasta térmica y Mantenimiento PC Desktop", "precio": 29800},
                {"servicio": "Instalación de Sistema Operativo (Windows/Linux) con Backup", "precio": 15000},
                {"servicio": "Limpieza profunda de hardware (PC Desktop)", "precio": 22500},
                {"servicio": "Diagnóstico de falla de encendido PC/Notebook", "precio": 12000},
                {"servicio": "Desbloqueo y flasheo de Netbooks del Gobierno", "precio": 18000},
                {"servicio": "Cambio de pantalla Notebook / Netbook", "precio": 35000},
                {"servicio": "Mantenimiento preventivo Consolas (PS4, PS5, Xbox One/Series)", "precio": 32000},
                {"servicio": "Reparación de Joystick (Drift, Botones, Batería)", "precio": 14000},
                {"servicio": "Reballing de placa de video / Consolas", "precio": 55000},
                {"servicio": "Cambio de módulo / Pantalla Celular", "precio": 45000},
                {"servicio": "Cambio de pin de carga (Celulares y Tablets)", "precio": 16000},
                {"servicio": "Cambio de batería celular", "precio": 20000},
                {"servicio": "Armado de PC Gamer a medida (solo mano de obra)", "precio": 40000},
                {"servicio": "Recuperación de datos de disco dañado (Nivel 1)", "precio": 50000},
                {"servicio": "Optimización de sistema y eliminación de virus", "precio": 13500}
            ]
            for s in initial_services:
                db.session.add(Service(servicio=s['servicio'], precio=s['precio']))
            db.session.commit()

# Llama a la inicialización antes del primer request si corremos la app
init_db()

# --- Endpoints ---

@app.route('/', methods=['GET'])
def index():
    services = Service.query.all()
    csv_lines = ["id,servicio,precio"]
    for s in services:
        csv_lines.append(f"{s.id},{s.servicio},{s.precio}")
    
    csv_data = "\n".join(csv_lines)
    return Response(csv_data, mimetype='text/plain')

@app.route('/api/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([s.to_dict() for s in services]), 200

@app.route('/api/services', methods=['POST'])
def add_service():
    data = request.get_json()
    
    if not data or 'servicio' not in data or 'precio' not in data:
        return jsonify({"error": "Faltan datos requeridos (servicio, precio)"}), 400
        
    servicio = str(data['servicio']).strip()
    precio = data['precio']
    
    if not servicio:
        return jsonify({"error": "El nombre del servicio no puede estar vacío"}), 400
        
    if not isinstance(precio, (int, float)):
        return jsonify({"error": "El precio debe ser un número válido"}), 400
        
    if precio < 0:
        return jsonify({"error": "El precio no puede ser negativo"}), 400
        
    new_service = Service(servicio=servicio, precio=precio)
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify({
        "message": "Servicio agregado al catálogo exitosamente",
        "service": new_service.to_dict()
    }), 201

@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart_items = CartItem.query.all()
    items_response = []
    total = 0
    
    for item in cart_items:
        subtotal = item.service.precio * item.cantidad
        total += subtotal
        items_response.append({
            "service_id": item.service.id,
            "servicio": item.service.servicio,
            "precio_unitario": item.service.precio,
            "cantidad": item.cantidad,
            "subtotal": subtotal
        })
            
    return jsonify({
        "items": items_response,
        "total": total
    }), 200

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    
    if not data or 'service_id' not in data or 'cantidad' not in data:
        return jsonify({"error": "Faltan datos requeridos en el body (service_id, cantidad)"}), 400
        
    service_id = data['service_id']
    cantidad = data['cantidad']
    
    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser un entero positivo"}), 400
        
    service = Service.query.get(service_id)
    if not service:
        return jsonify({"error": f"El servicio con id {service_id} no existe en el catálogo"}), 404
        
    cart_item = CartItem.query.filter_by(service_id=service_id).first()
    if cart_item:
        cart_item.cantidad += cantidad
    else:
        cart_item = CartItem(service_id=service_id, cantidad=cantidad)
        db.session.add(cart_item)
        
    db.session.commit()
        
    return jsonify({
        "message": "Servicio agregado al carrito",
        "service_id": service_id,
        "nueva_cantidad": cart_item.cantidad
    }), 201

@app.route('/api/cart/<int:service_id>', methods=['PUT'])
def update_cart_item(service_id):
    data = request.get_json()
    if not data or 'cantidad' not in data:
        return jsonify({"error": "Faltan datos requeridos (cantidad)"}), 400
        
    cantidad = data['cantidad']
    if not isinstance(cantidad, int) or cantidad < 0:
        return jsonify({"error": "La cantidad debe ser un número entero positivo o 0"}), 400
        
    cart_item = CartItem.query.filter_by(service_id=service_id).first()
    if not cart_item:
        return jsonify({"error": f"El servicio con id {service_id} no está en el carrito"}), 404
        
    if cantidad == 0:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item eliminado del carrito por cantidad 0"}), 200
        
    cart_item.cantidad = cantidad
    db.session.commit()
    return jsonify({"message": "Cantidad actualizada", "service_id": service_id, "nueva_cantidad": cantidad}), 200

@app.route('/api/cart/<int:service_id>', methods=['DELETE'])
def remove_from_cart(service_id):
    cart_item = CartItem.query.filter_by(service_id=service_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Servicio eliminado del carrito correctamente"}), 200
    else:
        return jsonify({"error": f"El servicio con id {service_id} no existe en el carrito"}), 404

@app.route('/api/cart', methods=['DELETE'])
def clear_cart():
    CartItem.query.delete()
    db.session.commit()
    return jsonify({"message": "Carrito vaciado por completo"}), 200

@app.route('/api/checkout', methods=['POST'])
def checkout():
    cart_items = CartItem.query.all()
    if not cart_items:
        return jsonify({"error": "El carrito está vacío, no se puede generar la orden"}), 400
        
    total = 0
    items_comprados = []
    
    # Crear nueva orden
    new_order = Order(total=0)
    db.session.add(new_order)
    db.session.flush() # Para obtener new_order.id
    
    for item in cart_items:
        subtotal = item.service.precio * item.cantidad
        total += subtotal
        
        order_item = OrderItem(
            order_id=new_order.id,
            service_id=item.service.id,
            precio_unitario=item.service.precio,
            cantidad=item.cantidad,
            subtotal=subtotal
        )
        db.session.add(order_item)
        
        items_comprados.append({
            "service_id": item.service.id,
            "servicio": item.service.servicio,
            "precio_unitario": item.service.precio,
            "cantidad": item.cantidad,
            "subtotal": subtotal
        })
            
    new_order.total = total
    
    # Vaciar carrito tras la compra
    CartItem.query.delete()
    db.session.commit()
    
    return jsonify({
        "message": "Compra finalizada con éxito",
        "order": {
            "order_id": new_order.id,
            "items": items_comprados,
            "total": total,
            "status": new_order.status
        }
    }), 201

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    orders_data = []
    for o in orders:
        items = OrderItem.query.filter_by(order_id=o.id).all()
        orders_data.append({
            "order_id": o.id,
            "total": o.total,
            "status": o.status,
            "items": [{"servicio": i.service.servicio, "cantidad": i.cantidad, "subtotal": i.subtotal} for i in items]
        })
    return jsonify(orders_data), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
