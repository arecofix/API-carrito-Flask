import pytest
from playwright.sync_api import Page, expect
import os
import threading
import time

# Asumiremos que el backend de flask ya está corriendo en http://127.0.0.1:5000 
# o puedes iniciar un live server en la misma máquina.
# También que el frontend se abre desde un live server o directamente el archivo HTML,
# pero como hace llamadas fetch a 'http://127.0.0.1:5000', el html puede estar en file:///

# Ruta al archivo HTML del frontend
FRONTEND_URL = f"file://{os.path.abspath('frontend/index.html')}"

def test_coffee_cart_e2e_flow(page: Page):
    """
    Prueba End-to-End del carrito de compras.
    Verifica cargar la página, agregar un servicio, comprobar el total y vaciar el carrito.
    """
    # 1. Abrir la página del frontend
    page.goto(FRONTEND_URL)
    
    # Asegurarse que se carguen los servicios (el título h1)
    expect(page.locator("h1")).to_contain_text("Servicios Técnicos")
    
    # 2. Esperar que los servicios se rendericen (esperar a que el contenedor tenga elementos)
    page.wait_for_selector(".service-card")
    
    # Contar los servicios renderizados (deberían ser 15)
    cards = page.locator(".service-card")
    expect(cards).to_have_count(15)
    
    # Vaciar el carrito previamente por si había algo de pruebas anteriores
    page.locator("#clear-cart-btn").click()
    # Esperar un poco a la red
    time.sleep(1)
    
    # 3. Agregar el primer servicio al carrito
    first_service_btn = cards.nth(0).locator("button")
    first_service_btn.click()
    
    # Esperar que el item aparezca en el carrito
    page.wait_for_selector(".cart-item")
    cart_items = page.locator(".cart-item")
    expect(cart_items).to_have_count(1)
    
    # Verificar que el total se actualizó (29800 del primer servicio)
    total_text = page.locator("#cart-total").inner_text()
    assert "29.800" in total_text or "29800" in total_text.replace(".", "")
    
    # 4. Incrementar cantidad (clic al botón de +)
    # Selecciona el botón '+' usando text='+' 
    page.locator("button:has-text('+')").first.click()
    time.sleep(1) # Esperar a que la API actualice
    
    total_text = page.locator("#cart-total").inner_text()
    # 29800 * 2 = 59600
    assert "59.600" in total_text or "59600" in total_text.replace(".", "")
    
    # 5. Eliminar el servicio (Vaciar carrito usando el tacho de basura general)
    page.locator("#clear-cart-btn").click()
    time.sleep(1)
    
    # Verificar que el carrito esté vacío
    expect(page.locator(".empty-cart-msg")).to_be_visible()
    total_text_final = page.locator("#cart-total").inner_text()
    assert "0" in total_text_final
