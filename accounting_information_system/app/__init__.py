from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from .routes_auth import auth_bp
    from .routes_dashboard import dashboard_bp
    from .routes_clients import clients_bp
    from .routes_invoices import invoices_bp
    from .routes_payments import payments_bp
    from .routes_portal import portal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(portal_bp)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Create DB tables
    with app.app_context():
        db.create_all()

    # Optional: custom error handler for 403
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    return app