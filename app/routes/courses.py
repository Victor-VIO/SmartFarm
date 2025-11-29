from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Course, CourseModule, CourseEnrollment

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/')
def browse():
    """Browse all courses"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    level = request.args.get('level', None)
    
    query = Course.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    
    courses = query.paginate(page=page, per_page=12)
    
    # Get unique categories and levels for filters
    all_categories = db.session.query(Course.category).distinct().all()
    categories = [c[0] for c in all_categories if c[0]]
    
    return render_template('courses/browse.html',
                         courses=courses,
                         categories=categories,
                         selected_category=category,
                         selected_level=level)

@courses_bp.route('/<int:course_id>')
def view_course(course_id):
    """View course details"""
    course = Course.query.get_or_404(course_id)
    
    if not course.is_published and (not current_user.is_authenticated or current_user.role != 'admin'):
        flash('This course is not available.', 'warning')
        return redirect(url_for('courses.browse'))
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if current_user.is_authenticated:
        enrollment = CourseEnrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course_id
        ).first()
        is_enrolled = enrollment is not None
    
    modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.order).all()
    
    return render_template('courses/view.html',
                         course=course,
                         modules=modules,
                         is_enrolled=is_enrolled,
                         enrollment=enrollment)

@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    """Enroll student in course"""
    course = Course.query.get_or_404(course_id)
    
    if not course.is_published:
        return jsonify({'error': 'Course not available'}), 404
    
    # Check if already enrolled
    existing = CourseEnrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already enrolled in this course'}), 400
    
    # Create enrollment
    enrollment = CourseEnrollment(
        student_id=current_user.id,
        course_id=course_id
    )
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in {course.title}!', 'success')
    return redirect(url_for('courses.view_course', course_id=course_id))

@courses_bp.route('/<int:course_id>/module/<int:module_id>')
@login_required
def view_module(course_id, module_id):
    """View course module"""
    course = Course.query.get_or_404(course_id)
    module = CourseModule.query.get_or_404(module_id)
    
    # Check if user is enrolled
    enrollment = CourseEnrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course.', 'warning')
        return redirect(url_for('courses.view_course', course_id=course_id))
    
    # Get all modules in order
    modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.order).all()
    
    return render_template('courses/module.html',
                         course=course,
                         module=module,
                         modules=modules,
                         enrollment=enrollment)

@courses_bp.route('/<int:course_id>/module/<int:module_id>/complete', methods=['POST'])
@login_required
def complete_module(course_id, module_id):
    """Mark module as complete"""
    try:
        enrollment = CourseEnrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled'}), 403
        
        course = Course.query.get_or_404(course_id)
        total_modules = CourseModule.query.filter_by(course_id=course_id).count()
        
        # Update progress only once per module
        if enrollment.modules_completed < total_modules:
            enrollment.modules_completed += 1
        
        # Calculate progress percentage
        enrollment.progress_percentage = (enrollment.modules_completed / total_modules) * 100
        
        # Check if course is completed
        course_completed = False
        certificate_earned = False
        
        if enrollment.modules_completed >= total_modules:
            enrollment.is_completed = True
            enrollment.certificate_earned = True
            enrollment.completed_at = datetime.utcnow()
            course_completed = True
            certificate_earned = True
            
            # Create certificate
            from app.models import Certificate
            import uuid
            
            existing_cert = Certificate.query.filter_by(
                student_id=current_user.id,
                course_id=course_id
            ).first()
            
            if not existing_cert:
                cert_code = f"SF-{uuid.uuid4().hex[:8].upper()}"
                certificate = Certificate(
                    student_id=current_user.id,
                    course_id=course_id,
                    certificate_code=cert_code
                )
                db.session.add(certificate)
        
        db.session.commit()
        
        message = 'Course Completed! Certificate Generated! 🎉' if course_completed else 'Module marked complete!'
        
        return jsonify({
            'success': True,
            'progress': enrollment.progress_percentage,
            'completed': enrollment.is_completed,
            'certificate_earned': certificate_earned,
            'message': message
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500