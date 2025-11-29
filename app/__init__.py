from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import DevelopmentConfig

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=DevelopmentConfig):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    
    with app.app_context():
        # Import models
        from app import models
        
        # Create database tables
        db.create_all()
        
        # Register blueprints (route groups)
        from app.routes import auth_bp, main_bp, courses_bp, mentorship_bp, dashboard_bp, admin_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(courses_bp)
        app.register_blueprint(mentorship_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(admin_bp)
    
    return app