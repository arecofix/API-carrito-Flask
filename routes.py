from flask import Blueprint, jsonify, request, Response
from extensions import db
from models import Service, CartItem, Order, OrderItem

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/api/csv', methods=['GET'])
def index_csv():
    """
    Lista de servicios disponibles en formato CSV.
    ---
    responses:
      200:
        description: Devuelve el catálogo en formato texto plano (CSV).
    """
    services = Service.query.all()
    csv_lines = ["id,servicio,precio"]
    for s in services:
        csv_lines.append(f"{s.id},{s.servicio},{s.precio}")
    
    csv_data = "\n".join(csv_lines)
    return Response(csv_data, mimetype='text/plain')

@api_bp.route('/api/services', methods=['GET'])
def get_services():
    """
    Retorna el catálogo completo de servicios en formato JSON.
    ---
    responses:
      200:
        description: Catálogo de servicios.
    """
    services = Service.query.all()
    return jsonify([s.to_dict() for s in services]), 200

@api_bp.route('/api/services', methods=['POST'])
def add_service():
    """
    Permite agregar un nuevo servicio al catálogo.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            servicio:
              type: string
              example: "Cambio de disco"
            precio:
              type: integer
              example: 25000
    responses:
      201:
        description: Servicio agregado correctamente.
      400:
        description: Error en los parámetros enviados (ej. precio negativo).
    """
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

@api_bp.route('/api/cart', methods=['GET'])
def get_cart():
    """
    Retorna los items actuales en el carrito y el total calculado.
    ---
    responses:
      200:
        description: Estado actual del carrito.
    """
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

@api_bp.route('/api/cart', methods=['POST'])
def add_to_cart():
    """
    Agrega un servicio al carrito o incrementa su cantidad.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            service_id:
              type: integer
              example: 1
            cantidad:
              type: integer
              example: 1
    responses:
      201:
        description: Añadido al carrito con éxito.
      400:
        description: Faltan datos o cantidad es inválida.
      404:
        description: Servicio no encontrado.
    """
    data = request.get_json()
    
    if not data or 'service_id' not in data or 'cantidad' not in data:
        return jsonify({"error": "Faltan datos requeridos en el body (service_id, cantidad)"}), 400
        
    service_id = data['service_id']
    cantidad = data['cantidad']
    
    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser un entero positivo"}), 400
        
    service = db.session.get(Service, service_id)
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

@api_bp.route('/api/cart/<int:service_id>', methods=['PUT'])
def update_cart_item(service_id):
    """
    Actualiza la cantidad exacta de un servicio. Si es 0, lo elimina.
    ---
    parameters:
      - in: path
        name: service_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            cantidad:
              type: integer
              example: 5
    responses:
      200:
        description: Cantidad actualizada exitosamente.
      400:
        description: Cantidad inválida.
      404:
        description: Servicio no encontrado en el carrito.
    """
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

@api_bp.route('/api/cart/<int:service_id>', methods=['DELETE'])
def remove_from_cart(service_id):
    """
    Elimina un servicio específico del carrito.
    ---
    parameters:
      - in: path
        name: service_id
        type: integer
        required: true
    responses:
      200:
        description: Eliminado correctamente.
      404:
        description: No encontrado.
    """
    cart_item = CartItem.query.filter_by(service_id=service_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Servicio eliminado del carrito correctamente"}), 200
    else:
        return jsonify({"error": f"El servicio con id {service_id} no existe en el carrito"}), 404

@api_bp.route('/api/cart', methods=['DELETE'])
def clear_cart():
    """
    Vacia el carrito por completo.
    ---
    responses:
      200:
        description: Carrito vaciado con éxito.
    """
    CartItem.query.delete()
    db.session.commit()
    return jsonify({"message": "Carrito vaciado por completo"}), 200

@api_bp.route('/api/checkout', methods=['POST'])
def checkout():
    """
    Procesa el carrito actual, genera una orden de compra y vacía el carrito.
    ---
    responses:
      201:
        description: Orden generada exitosamente.
      400:
        description: El carrito está vacío.
    """
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

@api_bp.route('/api/orders', methods=['GET'])
def get_orders():
    """
    Retorna el historial de órdenes de compra.
    ---
    responses:
      200:
        description: Historial de órdenes.
    """
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
