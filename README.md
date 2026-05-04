# API Carrito de Compras - SPA Backend

Este proyecto es la **Etapa 1** del desarrollo de una aplicación web (SPA) inspirada en un carrito de compras estilo "Coffee Cart", enfocada en servicios técnicos. Consiste en una robusta API RESTful construida con **Flask** (Python) que maneja toda la lógica del negocio, la gestión del carrito en memoria y un simulador de checkout.

## 🚀 Características Principales

*   **Catálogo de Servicios**: Listado de 15 servicios preconfigurados (reparación de PC, consolas, celulares, etc.).
*   **Gestión de Servicios**: Endpoint `POST` para agregar dinámicamente nuevos servicios con validación estricta de datos.
*   **Carrito Avanzado**: 
    *   Acumulación de cantidades al agregar un servicio repetido.
    *   Ajuste exacto de cantidades en un ítem (`PUT`).
    *   Eliminación individual o vaciado completo del carrito (`DELETE`).
*   **Checkout Simulator**: Generación automática de órdenes de compra, cálculos de totales y limpieza de sesión post-compra.
*   **Documentación Interactiva**: Integración nativa con **Flasgger (Swagger UI)**.
*   **Testing**: Alta cobertura de pruebas unitarias implementadas con `pytest`.

## 🛠️ Tecnologías Utilizadas
*   Python 3.x
*   Flask & Flask-CORS
*   Flasgger (OpenAPI/Swagger)
*   Pytest (Testing)

---

## 📖 Instrucciones de Uso (Paso a Paso)

Esta guía te ayudará a clonar, configurar, ejecutar y probar la API en tu entorno local. Ideal para evaluación o despliegue.

### 1. Clonar el repositorio
Abre tu terminal y ejecuta:
```bash
git clone https://github.com/arecofix/API-carrito-Flask.git
cd API-carrito-Flask
```

### 2. Configurar el Entorno Virtual (Recomendado)
Para evitar conflictos de dependencias, crea y activa un entorno virtual:

**En Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**En Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
Una vez activo el entorno virtual, instala los paquetes requeridos desde la raíz del proyecto:
```bash
pip install -r requirements.txt
```

### 4. Ejecutar las Pruebas Unitarias (Tests)
Para validar que toda la lógica de negocio y validaciones matemáticas (precios, inserciones, borrados) funcionan correctamente de forma automática:
```bash
python -m pytest
```
> *Deberías ver que los 11 tests pasan con 100% de éxito en verde.*

### 5. Iniciar el Servidor
Para levantar la API localmente en modo desarrollo, ejecuta:
```bash
python app.py
```
El servidor se iniciará y estará escuchando peticiones en `http://127.0.0.1:5000`.

### 6. Probar la API (Swagger UI)
No necesitas aplicaciones externas de terceros (como Postman) para probar el funcionamiento. Accede a la documentación interactiva abriendo la siguiente URL en tu navegador:

👉 **[http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)**

Desde allí podrás desplegar cada endpoint (ej: `GET /api/cart`), hacer clic en el botón blanco **"Try it out"**, luego en **"Execute"**, y visualizar las respuestas JSON reales del servidor en la parte inferior.

---

## 🔗 Estructura de Endpoints Principales

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/services` | Lista todos los servicios técnicos disponibles. |
| `POST` | `/api/services` | Crea un nuevo servicio (valida que el precio no sea negativo ni el string vacío). |
| `GET` | `/api/cart` | Devuelve el estado actual del carrito y el subtotal calculado general. |
| `POST` | `/api/cart` | Agrega un servicio al carrito o incrementa la cantidad si ya existe. |
| `PUT` | `/api/cart/{service_id}` | Actualiza a una cantidad exacta. Si se envía cantidad 0, lo elimina. |
| `DELETE` | `/api/cart/{service_id}` | Elimina el servicio especificado del carrito. |
| `DELETE` | `/api/cart` | Vacía todo el contenido del carrito. |
| `POST` | `/api/checkout` | Genera una orden de compra, guarda el registro y limpia el carrito. |
| `GET` | `/api/orders` | Muestra el historial de todas las órdenes de compras finalizadas. |
