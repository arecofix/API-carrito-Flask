from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
# Configuración básica de Swagger
app.config['SWAGGER'] = {
    'title': 'Carrito de Compras API',
    'uiversion': 3
}
swagger = Swagger(app)

# --- Datos en memoria (Persistencia) ---

# Catálogo de servicios técnicos
services_catalog = [
    {
        "id": 1,
        "servicio": "Cambio de Pasta térmica y Mantenimiento",
        "precio": 29800
    },
    {
        "id": 2,
        "servicio": "Instalación de Sistema Operativo (Windows/Linux)",
        "precio": 15000
    },
    {
        "id": 3,
        "servicio": "Limpieza profunda de hardware (PC Desktop)",
        "precio": 22500
    },
    {
        "id": 4,
        "servicio": "Diagnóstico de falla de encendido",
        "precio": 12000
    }
]

# Carrito de compras
# Formato: { item_id: {"service_id": id, "cantidad": cant} }
cart = {}
cart_item_counter = 1

# --- Endpoints ---

@app.route('/', methods=['GET'])
def index():
    """
    Lista de servicios disponibles en formato CSV.
    ---
    responses:
      200:
        description: Retorna el catálogo en formato texto plano CSV.
    """
    csv_lines = ["id,servicio,precio"]
    for s in services_catalog:
        csv_lines.append(f"{s['id']},{s['servicio']},{s['precio']}")
    
    csv_data = "\n".join(csv_lines)
    return Response(csv_data, mimetype='text/plain')

@app.route('/api/services', methods=['GET'])
def get_services():
    """
    Retorna el catálogo completo de servicios en formato JSON.
    ---
    responses:
      200:
        description: Lista de servicios
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: ID del servicio
              servicio:
                type: string
                description: Nombre del servicio
              precio:
                type: integer
                description: Precio del servicio
    """
    return jsonify(services_catalog), 200

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """
    Retorna los items actuales en el carrito y el total calculado de la compra.
    ---
    responses:
      200:
        description: Estado del carrito y total de la compra
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  item_id:
                    type: integer
                  service_id:
                    type: integer
                  servicio:
                    type: string
                  precio_unitario:
                    type: integer
                  cantidad:
                    type: integer
                  subtotal:
                    type: integer
            total:
              type: integer
              description: Precio total de la compra
    """
    items_response = []
    total = 0
    
    for item_id, item_data in cart.items():
        # Buscar el servicio en el catálogo para armar la respuesta
        service = next((s for s in services_catalog if s["id"] == item_data["service_id"]), None)
        if service:
            subtotal = service["precio"] * item_data["cantidad"]
            total += subtotal
            
            items_response.append({
                "item_id": item_id,
                "service_id": service["id"],
                "servicio": service["servicio"],
                "precio_unitario": service["precio"],
                "cantidad": item_data["cantidad"],
                "subtotal": subtotal
            })
            
    return jsonify({
        "items": items_response,
        "total": total
    }), 200

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """
    Permite agregar un servicio al carrito.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            service_id:
              type: integer
              description: ID del servicio a agregar
            cantidad:
              type: integer
              description: Cantidad del servicio
    responses:
      201:
        description: Servicio agregado al carrito exitosamente
      400:
        description: Datos inválidos o faltantes
      404:
        description: Servicio no encontrado en el catálogo
    """
    global cart_item_counter
    
    data = request.get_json()
    
    if not data or 'service_id' not in data or 'cantidad' not in data:
        return jsonify({"error": "Faltan datos requeridos en el body (service_id, cantidad)"}), 400
        
    service_id = data['service_id']
    cantidad = data['cantidad']
    
    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser un entero positivo"}), 400
        
    # Verificar si el servicio existe en el catálogo
    service_exists = any(s["id"] == service_id for s in services_catalog)
    if not service_exists:
        return jsonify({"error": f"El servicio con id {service_id} no existe en el catálogo"}), 404
        
    # Crear un nuevo ID de item para esta adición al carrito
    item_id = cart_item_counter
    cart[item_id] = {
        "service_id": service_id,
        "cantidad": cantidad
    }
    
    cart_item_counter += 1
    
    return jsonify({
        "message": "Servicio agregado al carrito",
        "item_id": item_id
    }), 201

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """
    Permite eliminar un servicio específico del carrito.
    ---
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: ID del item dentro del carrito
    responses:
      200:
        description: Item eliminado correctamente
      404:
        description: Item no encontrado en el carrito
    """
    if item_id in cart:
        del cart[item_id]
        return jsonify({"message": "Item eliminado del carrito correctamente"}), 200
    else:
        return jsonify({"error": f"El item con id {item_id} no existe en el carrito"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
