import os
from flask import Flask, jsonify, send_from_directory, session
from flask_cors import CORS
from dotenv import load_dotenv
from database import init_db, db
from models import Rubro, Entidad, Campo, Empresa, ConfigEmpresa, Usuario, Notificacion, Tarea
from routes import api_bp

load_dotenv()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'uploads')

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'siges-secret-2026')

    init_db(app)
    CORS(app, supports_credentials=True)
    app.register_blueprint(api_bp)

    # Crear carpeta de uploads si no existe
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ── Servir frontend ──────────────────────────────────────────
    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/setup')
    def setup():
        return send_from_directory('../frontend', 'setup.html')

    @app.route('/dashboard')
    def dashboard():
        return send_from_directory('../frontend', 'dashboard.html')

    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    @app.route('/api/health')
    def health():
        try:
            db.engine.connect()
            return jsonify({'status': 'ok', 'database': 'conectada'})
        except Exception as e:
            return jsonify({'status': 'error', 'database': str(e)})

    # Ruta para archivos estáticos (DEBE IR AL FINAL)
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('../frontend', path)

    return app  # <--- el return app debe estar al final, después de todas las rutas

app = create_app()  # <--- ahora esto está bien ubicado

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Base de datos conectada y tablas creadas")
        print(f"📌 Conectado a: {os.getenv('DATABASE_URL')}")
    app.run(debug=True, port=5000)