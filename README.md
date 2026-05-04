# Aplicación Web SPA - Carrito de Compras de Servicios Técnicos

Este repositorio contiene el proyecto finalizado (Etapa 1 y Etapa 2) para el Desarrollo de una Aplicación Web Single Page Application (SPA), inspirada en "Coffee Cart".

## Arquitectura del Proyecto (Clean Architecture & Desacoplada)

El proyecto está diseñado siguiendo una **arquitectura cliente-servidor completamente desacoplada** e internamente utiliza principios de **Clean Architecture y App Factory Pattern**.

Esto significa que el backend (la API) y el frontend (la interfaz de usuario) operan de forma independiente, comunicándose exclusivamente a través de peticiones HTTP (REST). A nivel backend, las responsabilidades están separadas en múltiples archivos.

### Estructura de Carpetas

```
API-carrito-flask/
├── app.py                # App Factory: Inicialización modular de Flask
├── extensions.py         # Instanciación de extensiones (SQLAlchemy, Swagger, CORS)
├── models.py             # Modelos de Base de Datos (Servicios, Carrito, Órdenes)
├── routes.py             # Blueprints y lógica de ruteo RESTful
├── carrito.db            # Base de Datos: SQLite autogenerada por SQLAlchemy
├── requirements.txt      # Dependencias del backend (incluye gunicorn para deploy)
├── e2e_test.py           # Testing E2E con Playwright
├── test_app.py           # Testing unitario con Pytest
│
└── frontend/             # Frontend (SPA)
    ├── index.html        # Estructura principal
    ├── styles.css        # Diseño UI (Glassmorphism, animaciones, dark mode)
    └── app.js            # Lógica JS Vanilla (Fetch API a backend)
```

## Tecnologías Implementadas

### Backend (Etapa 1)

- **Python 3 / Flask:** Framework ligero para construir las APIs.
- **Flask-SQLAlchemy (SQLite):** ORM utilizado para persistencia de datos relacional.
- **Flasgger:** Documentación interactiva autogenerada de la API (Swagger UI).
- **Flask-CORS:** Habilita peticiones cruzadas desde el frontend.
- **Gunicorn:** WSGI HTTP Server preparado para el deploy a producción (Render/Railway).

### Frontend (Etapa 2)

- **HTML5 & CSS3 (Vainilla):** Interfaz premium y moderna utilizando _Glassmorphism_, gradientes sutiles y micro-animaciones. Sin dependencias externas pesadas.
- **JavaScript (Vainilla):** Manejo asíncrono usando `Fetch API` para sincronizar el estado del carrito dinámicamente con el servidor.

### Testing

- **Pytest:** Suite de pruebas unitarias cubriendo el 100% de los flujos de la API con bases de datos en memoria para el testeo.
- **Playwright (pytest-playwright):** Herramienta para realizar pruebas _End-to-End_ simulando un navegador real manipulando la SPA (abre el carrito, agrega servicios, actualiza la cantidad y verifica los totales asíncronos).

---

## Dificultades Encontradas y Soluciones

1. **Persistencia Compartida vs. Testing:**
   - _Dificultad:_ Al pasar de memoria temporal a base de datos SQLite, las pruebas unitarias comenzaban a pisar los datos reales del catálogo o fallaban al buscar dependencias circulares.
   - _Solución:_ Se implementó el patrón `Application Factory` en Flask. Esto permite crear instancias aisladas de la aplicación para `pytest` utilizando una base de datos temporal en memoria (`sqlite:///:memory:`), lo que garantiza la idempotencia de las pruebas y un entorno 100% limpio por cada ejecución.
2. **CORS (Cross-Origin Resource Sharing):**
   - _Dificultad:_ Al separar el frontend y abrirlo localmente vía `file://` o un Live Server, las peticiones HTTP eran bloqueadas por el navegador debido a políticas de seguridad.
   - _Solución:_ Se integró e inicializó `flask-cors` en `extensions.py` para permitir tráfico cruzado en las API expuestas.
3. **Manejo Dinámico de Cantidades en el Frontend:**
   - _Dificultad:_ Alinear la velocidad de los clics en los botones "Sumar/Restar" del frontend con la respuesta asíncrona del backend y base de datos, sin generar desincronización de totales.
   - _Solución:_ Se implementaron llamadas `async/await` estructuradas. La interfaz gráfica se bloquea por fracciones de segundo e inmediatamente se renderiza (`loadCart()`) con la fuente única de verdad retornada por el servidor, asegurando que el DOM y la Base de datos tengan siempre los mismos números.

---

## 📖 Instrucciones para Ejecución y Deploy

### 1. Ejecución Local

1. Activa tu entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # En Windows
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Ejecuta el servidor de Flask:
   ```bash
   python app.py
   ```
   _Swagger interactivo en `http://127.0.0.1:5000/apidocs`._
4. Abre el archivo `/frontend/index.html` en tu navegador.
5. Para correr los tests E2E y unitarios:
   ```bash
   pytest test_app.py
   pytest e2e_test.py
   ```
