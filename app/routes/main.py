from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.models import Course, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    featured_courses = Course.query.filter_by(is_published=True).limit(6).all()
    mentor_count = User.query.filter_by(role='mentor').count()
    student_count = User.query.filter_by(role='student').count()
    
    stats = {
        'courses': Course.query.filter_by(is_published=True).count(),
        'students': student_count,
        'mentors': mentor_count,
    }
    
    return render_template('main/index.html', 
                         featured_courses=featured_courses,
                         stats=stats)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # In production, send email here
        # For now, just show a success message
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('main/contact.html')

@main_bp.route('/terms')
def terms():
    """Terms of service"""
    return render_template('main/terms.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy"""
    return render_template('main/privacy.html')
