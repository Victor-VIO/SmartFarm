from flask import Blueprint

# Import route modules
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.courses import courses_bp
from app.routes.mentorship import mentorship_bp
from app.routes.dashboard import dashboard_bp
from app.routes.admin import admin_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'courses_bp',
    'mentorship_bp',
    'dashboard_bp',
    'admin_bp'
]
