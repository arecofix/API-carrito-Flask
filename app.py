import os
from flask import Flask
from extensions import db, swagger, cors
from routes import api_bp
from models import Service

def create_app():
    # Configuramos Flask para servir los archivos estáticos desde /frontend
    app = Flask(__name__, static_folder='frontend', static_url_path='')
    
    # Configuración Base de Datos SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'carrito.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración Swagger
    app.config['SWAGGER'] = {
        'title': 'Carrito de Compras API',
        'uiversion': 3,
        'validatorUrl': ''  # Evita el error "Uncaught ReferenceError: None is not defined"
    }
    
    # Inicializar extensiones
    db.init_app(app)
    swagger.init_app(app)
    cors.init_app(app)
    
    # Registrar rutas
    app.register_blueprint(api_bp)
    
    # Inicialización de Base de Datos
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

    # Ruta raíz que sirve el Frontend SPA automáticamente
    @app.route('/')
    def serve_frontend():
        return app.send_static_file('index.html')

    # Ignorar silenciosamente la petición del favicon para que no tire error 404
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
