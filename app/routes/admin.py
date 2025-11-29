from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Course, CourseModule
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin check decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    users_count = User.query.count()
    courses_count = Course.query.count()
    students_count = User.query.filter_by(role='student').count()
    mentors_count = User.query.filter_by(role='mentor').count()
    
    stats = {
        'total_users': users_count,
        'total_courses': courses_count,
        'total_students': students_count,
        'total_mentors': mentors_count,
    }
    
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_courses=recent_courses,
                         recent_users=recent_users)

@admin_bp.route('/courses')
@login_required
@admin_required
def manage_courses():
    """Manage courses"""
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page=page, per_page=20)
    
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_course():
    """Create new course"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        level = request.form.get('level', 'beginner')
        duration_weeks = request.form.get('duration_weeks', 4, type=int)
        instructor = request.form.get('instructor')
        video_url = request.form.get('video_url')
        
        if not title or not description or not category:
            flash('Title, description, and category are required.', 'danger')
            return redirect(url_for('admin.create_course'))
        
        course = Course(
            title=title,
            description=description,
            category=category,
            level=level,
            duration_weeks=duration_weeks,
            instructor=instructor,
            video_url=video_url,
            is_published=False
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course "{title}" created successfully!', 'success')
        return redirect(url_for('admin.edit_course', course_id=course.id))
    
    return render_template('admin/create_course.html')

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    """Edit course"""
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.category = request.form.get('category')
        course.level = request.form.get('level', 'beginner')
        course.duration_weeks = request.form.get('duration_weeks', 4, type=int)
        course.instructor = request.form.get('instructor')
        course.video_url = request.form.get('video_url')
        course.is_published = 'is_published' in request.form
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.manage_courses'))
    
    return render_template('admin/edit_course.html', course=course)

@admin_bp.route('/courses/<int:course_id>/modules', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_modules(course_id):
    """Manage course modules"""
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        order = request.form.get('order', type=int, default=1)
        video_url = request.form.get('video_url')
        content = request.form.get('content')
        
        if not title:
            flash('Module title is required.', 'danger')
            return redirect(url_for('admin.manage_modules', course_id=course_id))
        
        module = CourseModule(
            course_id=course_id,
            title=title,
            description=description,
            order=order,
            video_url=video_url,
            content=content
        )
        
        db.session.add(module)
        db.session.commit()
        
        flash('Module added successfully!', 'success')
        return redirect(url_for('admin.manage_modules', course_id=course_id))
    modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.order).all()
    return render_template('admin/manage_modules.html', course=course, modules=modules)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', None)
    query = User.query
    if role:
        query = query.filter_by(role=role)
    users = query.paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users, selected_role=role)

@admin_bp.route('/mentors')
@login_required
@admin_required
def manage_mentors():
    """Manage mentors"""
    page = request.args.get('page', 1, type=int)
    mentors = User.query.filter_by(role='mentor').paginate(page=page, per_page=20)
    return render_template('admin/mentors.html', mentors=mentors)

@admin_bp.route('/users/int:user_id/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.manage_users'))