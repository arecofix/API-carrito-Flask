# Aplicación Web SPA - Carrito de Compras de Servicios Técnicos

Este repositorio contiene el proyecto finalizado de ambas etapas (Etapa 1 y Etapa 2) para el Desarrollo de una Aplicación Web Single Page Application (SPA), inspirada en "Coffee Cart".

## 🏗️ Arquitectura del Proyecto (Desacoplada)

El proyecto está diseñado siguiendo una **arquitectura cliente-servidor completamente desacoplada**. Esto significa que el backend (la API) y el frontend (la interfaz de usuario) operan de forma independiente, comunicándose exclusivamente a través de peticiones HTTP (REST). 

Esta decisión arquitectónica permite:
1. Desplegar el frontend y el backend en servidores distintos.
2. Hacer modificaciones en la interfaz sin afectar la lógica de negocio ni la base de datos.
3. Evaluar la Etapa 1 (solo backend) de forma aislada a través de herramientas como Swagger.

### Estructura de Carpetas

```
API-carrito-flask/
├── app.py                # Backend: Servidor Flask y lógica RESTful
├── carrito.db            # Base de Datos: SQLite autogenerada por SQLAlchemy
├── requirements.txt      # Dependencias del backend
├── e2e_test.py           # Testing E2E con Playwright
│
└── frontend/             # Frontend (SPA)
    ├── index.html        # Estructura principal
    ├── styles.css        # Diseño UI (estilo oscuro de software ágil)
    └── app.js            # Lógica JS Vanilla (Fetch API a http://127.0.0.1:5000)
```

## 🛠️ Tecnologías Implementadas

### Backend (Etapa 1)
*   **Python 3 / Flask:** Framework ligero para construir las APIs.
*   **Flask-SQLAlchemy (SQLite):** ORM utilizado para persistencia real de datos (Servicios, Carrito y Órdenes).
*   **Flasgger:** Documentación interactiva autogenerada de la API (Swagger UI).
*   **Flask-CORS:** Habilita peticiones cruzadas desde el frontend.

### Frontend (Etapa 2)
*   **HTML5 & CSS3 (Vainilla):** Interfaz limpia, oscura ("Dark Mode") y ágil. Sin dependencias externas pesadas.
*   **JavaScript (Vainilla):** Manejo asíncrono usando `Fetch API` para sincronizar el estado del carrito dinámicamente con el servidor.

### Testing
*   **Playwright (pytest-playwright):** Herramienta para realizar pruebas *End-to-End* simulando un navegador real manipulando la SPA.

---

## 📖 Instrucciones para Ejecución Local

Dado que la arquitectura es desacoplada, el backend y el frontend se ejecutan/sirven por separado.

### 1. Iniciar el Backend (Servidor Flask)

1. Crea y activa tu entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # En Windows
   source venv/bin/activate  # En Linux/Mac
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   pip install flask-sqlalchemy playwright pytest-playwright
   ```
3. Ejecuta el servidor de Flask:
   ```bash
   python app.py
   ```
   *El servidor iniciará en `http://127.0.0.1:5000`. La base de datos SQLite (`carrito.db`) se generará automáticamente con el catálogo precargado. Puedes ver el Swagger en `http://127.0.0.1:5000/apidocs`.*

### 2. Iniciar el Frontend (SPA)

Al no usar Node.js/Frameworks pesados, puedes iniciar el frontend de la manera más sencilla posible:
1. Navega a la carpeta `/frontend`.
2. Simplemente haz doble clic en el archivo `index.html` para abrirlo en tu navegador (`file:///.../frontend/index.html`).
3. O si utilizas VS Code, instala la extensión "Live Server" y dale a "Go Live" en `index.html`.

*Nota: La interfaz comenzará a realizar llamadas `fetch` a `http://127.0.0.1:5000`. Asegúrate de que el backend esté corriendo simultáneamente.*

### 3. Ejecutar Pruebas E2E (Playwright)

Para validar el flujo completo automatizado en la UI:

1. Asegúrate de tener instalado Playwright y sus navegadores base:
   ```bash
   playwright install chromium
   ```
2. Ejecuta el script de pruebas en una terminal separada:
   ```bash
   pytest e2e_test.py
   ```
   *Playwright levantará un navegador invisible, abrirá el frontend, agregará un servicio, validará la suma del total calculada por el backend y limpiará el carrito.*
