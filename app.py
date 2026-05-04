import os
from flask import Flask
from extensions import db, swagger, cors
from routes import api_bp
from models import Service

def create_app():
    # Configuramos Flask para servir los archivos estáticos desde /frontend
    app = Flask(__name__, static_folder='frontend', static_url_path='')
    
    # Configuración SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'carrito.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    app.config['Enrico'] = {
        'title': 'Carrito de Compras API',
        'uiversion': 3,
        'validatorUrl': ''
    }
    
    # Inicializar extensiones
    db.init_app(app)
    swagger.init_app(app)
    cors.init_app(app)
    
    app.register_blueprint(api_bp)
    
    # Base de Datos
    with app.app_context():
        db.create_all()
        # Agregar servicios iniciales si la tabla está vacía
        if Service.query.count() == 0:
            initial_services = [
                {"servicio": "Mantenimiento Preventivo PC Desktop", "precio": 25000},
                {"servicio": "Limpieza Profunda de Hardware y Pasta Térmica", "precio": 29800},
                {"servicio": "Instalación de SO (Windows/Linux) con Backup", "precio": 18000},
                {"servicio": "Diagnóstico de Falla de Encendido (PC/Notebook)", "precio": 12000},
                {"servicio": "Armado de PC Gamer a Medida", "precio": 40000},
                {"servicio": "Actualización de Componentes (RAM / SSD)", "precio": 15000},
                {"servicio": "Desbloqueo de Netbooks Escolares", "precio": 18000},
                {"servicio": "Cambio de Pantalla (Notebook/Netbook)", "precio": 35000},
                {"servicio": "Cambio de Teclado (Notebook)", "precio": 22000},
                {"servicio": "Reparación de Bisagras y Carcasa", "precio": 28000},
                {"servicio": "Mantenimiento Consolas (PS4 / PS5)", "precio": 32000},
                {"servicio": "Mantenimiento Consolas (Xbox One / Series)", "precio": 32000},
                {"servicio": "Reparación de Joystick - Fix Drift", "precio": 14000},
                {"servicio": "Reballing de Placa de Video", "precio": 65000},
                {"servicio": "Micro-soldadura en Placa Madre (SMD)", "precio": 45000},
                {"servicio": "Reparación de Fuente de Alimentación", "precio": 20000},
                {"servicio": "Cambio de Módulo de Pantalla (Smartphone)", "precio": 45000},
                {"servicio": "Cambio de Pin de Carga (Celular/Tablet)", "precio": 16000},
                {"servicio": "Reemplazo de Batería Interna (Celular)", "precio": 22000},
                {"servicio": "Recuperación de Datos (Borrado Accidental)", "precio": 30000},
                {"servicio": "Recuperación de Datos de Disco Dañado", "precio": 55000},
                {"servicio": "Eliminación de Virus y Optimización", "precio": 13500},
                {"servicio": "Instalación de Software de Diseño/Arquitectura", "precio": 15000},
                {"servicio": "Configuración de Redes y Routers WiFi", "precio": 18000}
            ]
            for s in initial_services:
                db.session.add(Service(servicio=s['servicio'], precio=s['precio']))
            db.session.commit()

    @app.route('/')
    def serve_frontend():
        return app.send_static_file('index.html')
    
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
