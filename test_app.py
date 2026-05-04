import pytest
import json
from app import app, cart

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Limpiar el carrito antes de cada prueba para tener un estado consistente
        cart.clear()
        yield client

def test_index_csv(client):
    """Prueba que la ruta raíz devuelve un CSV con los servicios."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.mimetype == 'text/plain'
    
    data = response.data.decode('utf-8')
    assert "id,servicio,precio" in data
    assert "1,Cambio de Pasta térmica y Mantenimiento,29800" in data

def test_get_services(client):
    """Prueba que se lista el catálogo en formato JSON."""
    response = client.get('/api/services')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 4
    assert data[0]['servicio'] == "Cambio de Pasta térmica y Mantenimiento"

def test_add_to_cart_success(client):
    """Prueba que un servicio existente se puede agregar al carrito."""
    response = client.post('/api/cart', json={
        "service_id": 1,
        "cantidad": 2
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "Servicio agregado al carrito"
    assert "item_id" in data

def test_add_to_cart_missing_data(client):
    """Prueba que falta de datos devuelve error 400."""
    response = client.post('/api/cart', json={
        "service_id": 1
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_add_to_cart_invalid_service(client):
    """Prueba que agregar un servicio inexistente devuelve error 404."""
    response = client.post('/api/cart', json={
        "service_id": 999,
        "cantidad": 1
    })
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data

def test_get_cart_and_total(client):
    """Prueba la obtención de los items del carrito y el cálculo del total."""
    # Agregamos dos servicios diferentes
    client.post('/api/cart', json={"service_id": 1, "cantidad": 1}) # 29800 * 1
    client.post('/api/cart', json={"service_id": 2, "cantidad": 2}) # 15000 * 2 = 30000
    
    response = client.get('/api/cart')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data["items"]) == 2
    assert data["total"] == 59800 # 29800 + 30000

def test_remove_from_cart(client):
    """Prueba que un item se puede eliminar del carrito correctamente."""
    # Agregamos un servicio al carrito primero
    add_response = client.post('/api/cart', json={"service_id": 1, "cantidad": 1})
    item_id = json.loads(add_response.data)["item_id"]
    
    # Verificamos que se puede eliminar
    del_response = client.delete(f'/api/cart/{item_id}')
    assert del_response.status_code == 200
    assert json.loads(del_response.data)["message"] == "Item eliminado del carrito correctamente"
    
    # Verificamos que ya no está en el carrito
    get_response = client.get('/api/cart')
    data = json.loads(get_response.data)
    assert len(data["items"]) == 0

def test_remove_from_cart_not_found(client):
    """Prueba que eliminar un item que no existe devuelve error 404."""
    response = client.delete('/api/cart/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
