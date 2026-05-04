import pytest
import json
from app import app, cart, orders

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        cart.clear()
        orders.clear()
        yield client

def test_index_csv(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "1,Cambio de Pasta térmica y Mantenimiento PC Desktop,29800" in response.data.decode('utf-8')

def test_get_services(client):
    response = client.get('/api/services')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 15
    assert data[0]['servicio'] == "Cambio de Pasta térmica y Mantenimiento PC Desktop"

def test_add_service_success(client):
    response = client.post('/api/services', json={
        "servicio": "Cambio de disco HDD a SSD",
        "precio": 25000
    })
    assert response.status_code == 201

def test_add_service_negative_price(client):
    response = client.post('/api/services', json={
        "servicio": "Servicio Invalido",
        "precio": -500
    })
    assert response.status_code == 400

def test_add_to_cart_success_and_accumulate(client):
    # Add once
    res1 = client.post('/api/cart', json={"service_id": 1, "cantidad": 2})
    assert res1.status_code == 201
    
    # Add same product again
    res2 = client.post('/api/cart', json={"service_id": 1, "cantidad": 1})
    data = json.loads(res2.data)
    assert data["nueva_cantidad"] == 3

def test_update_cart_item(client):
    client.post('/api/cart', json={"service_id": 1, "cantidad": 1})
    res = client.put('/api/cart/1', json={"cantidad": 5})
    assert res.status_code == 200
    assert json.loads(res.data)["nueva_cantidad"] == 5

def test_update_cart_item_to_zero_removes_it(client):
    client.post('/api/cart', json={"service_id": 1, "cantidad": 1})
    res = client.put('/api/cart/1', json={"cantidad": 0})
    assert res.status_code == 200
    
    res_get = client.get('/api/cart')
    data = json.loads(res_get.data)
    assert len(data["items"]) == 0

def test_remove_from_cart(client):
    client.post('/api/cart', json={"service_id": 1, "cantidad": 1})
    res = client.delete('/api/cart/1')
    assert res.status_code == 200

def test_clear_cart(client):
    client.post('/api/cart', json={"service_id": 1, "cantidad": 1})
    client.post('/api/cart', json={"service_id": 2, "cantidad": 2})
    res = client.delete('/api/cart')
    assert res.status_code == 200
    
    res_get = client.get('/api/cart')
    assert len(json.loads(res_get.data)["items"]) == 0

def test_checkout(client):
    client.post('/api/cart', json={"service_id": 1, "cantidad": 1}) # 29800
    client.post('/api/cart', json={"service_id": 2, "cantidad": 2}) # 15000 * 2 = 30000
    
    res = client.post('/api/checkout')
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data["order"]["total"] == 59800
    assert len(data["order"]["items"]) == 2
    
    # Cart should be empty
    res_get = client.get('/api/cart')
    assert len(json.loads(res_get.data)["items"]) == 0

def test_checkout_empty_cart(client):
    res = client.post('/api/checkout')
    assert res.status_code == 400
