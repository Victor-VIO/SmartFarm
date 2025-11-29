# from flask import send_file
# from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
# from flask_login import login_required, current_user
# from app import db
# from app.models import User, CourseEnrollment, Course, MentorshipRequest
# from io import BytesIO
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.pdfgen import canvas
# from flask import send_file
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, CourseEnrollment, Course, MentorshipRequest
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """User dashboard"""
    # Get enrolled courses
    enrollments = CourseEnrollment.query.filter_by(student_id=current_user.id).all()
    courses = [enrollment.course for enrollment in enrollments]
    
    # Get mentorship info
    if current_user.role == 'student':
        mentorships = MentorshipRequest.query.filter_by(student_id=current_user.id).all()
    else:
        mentorships = MentorshipRequest.query.filter_by(mentor_id=current_user.id).all()
    
    stats = {
        'courses_enrolled': len(enrollments),
        'courses_completed': sum(1 for e in enrollments if e.is_completed),
        'mentorship_active': sum(1 for m in mentorships if m.status == 'accepted'),
    }
    
    return render_template('dashboard/index.html',
                         courses=courses,
                         enrollments=enrollments,
                         mentorships=mentorships,
                         stats=stats)

@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('dashboard/profile.html', user=current_user)

@dashboard_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.bio = request.form.get('bio')
        
        if current_user.role == 'mentor':
            current_user.expertise = request.form.get('expertise')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('dashboard/edit_profile.html', user=current_user)

@dashboard_bp.route('/settings')
@login_required
def settings():
    """User settings"""
    return render_template('dashboard/settings.html', user=current_user)

@dashboard_bp.route('/theme/<theme>', methods=['POST'])
@login_required
def set_theme(theme):
    """Change theme (light/dark)"""
    if theme not in ['light', 'dark']:
        return jsonify({'error': 'Invalid theme'}), 400
    
    current_user.theme = theme
    db.session.commit()
    
    return jsonify({'success': True, 'theme': theme})

@dashboard_bp.route('/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(old_password):
            flash('Old password is incorrect.', 'danger')
            return redirect(url_for('dashboard.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('dashboard.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard.settings'))
    
    return render_template('dashboard/change_password.html')

@dashboard_bp.route('/certificates')
@login_required
def certificates():
    """View earned certificates"""
    from app.models import Certificate
    
    certificates = Certificate.query.filter_by(student_id=current_user.id).all()
    
    return render_template('dashboard/certificates.html', certificates=certificates)

@dashboard_bp.route('/certificate/<cert_code>/download', methods=['GET'])
@login_required
def download_certificate(cert_code):
    """Download certificate as PDF"""
    from app.models import Certificate
    
    cert = Certificate.query.filter_by(certificate_code=cert_code).first()
    
    if not cert or cert.student_id != current_user.id:
        flash('Certificate not found.', 'danger')
        return redirect(url_for('dashboard.certificates'))
    
    # Create PDF in memory
    pdf_buffer = BytesIO()
    
    # Create canvas (letter size, landscape)
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(11*72, 8.5*72))
    
    # Set background color (light gold)
    pdf_canvas.setFillColor(colors.HexColor('#fef3c7'))
    pdf_canvas.rect(0, 0, 11*72, 8.5*72, fill=1, stroke=0)
    
    # Set border
    pdf_canvas.setStrokeColor(colors.HexColor('#d4af37'))
    pdf_canvas.setLineWidth(3)
    pdf_canvas.rect(20, 20, 11*72-40, 8.5*72-40)
    
    # Title
    pdf_canvas.setFont("Helvetica-Bold", 48)
    pdf_canvas.setFillColor(colors.HexColor('#92400e'))
    pdf_canvas.drawCentredString(11*72/2, 7.5*72, "Certificate of Completion")
    
    # Subtitle
    pdf_canvas.setFont("Helvetica", 16)
    pdf_canvas.setFillColor(colors.HexColor('#b45309'))
    pdf_canvas.drawCentredString(11*72/2, 7*72, "SmartFarm Training Hub")
    
    # "This certifies that"
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.setFillColor(colors.HexColor('#78350f'))
    pdf_canvas.drawCentredString(11*72/2, 5.5*72, "This is to certify that")
    
    # Student name
    pdf_canvas.setFont("Helvetica-Bold", 36)
    pdf_canvas.setFillColor(colors.HexColor('#92400e'))
    pdf_canvas.drawCentredString(11*72/2, 4.8*72, current_user.full_name or current_user.username)
    
    # "has successfully completed"
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.setFillColor(colors.HexColor('#78350f'))
    pdf_canvas.drawCentredString(11*72/2, 4.2*72, "has successfully completed the course")
    
    # Course title
    pdf_canvas.setFont("Helvetica-Bold", 18)
    pdf_canvas.setFillColor(colors.HexColor('#b45309'))
    pdf_canvas.drawCentredString(11*72/2, 3.6*72, cert.course.title)
    
    # Course details
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.setFillColor(colors.HexColor('#78350f'))
    pdf_canvas.drawCentredString(11*72/2, 3.2*72, f"Category: {cert.course.category}")
    pdf_canvas.drawCentredString(11*72/2, 2.9*72, f"Duration: {cert.course.duration_weeks} weeks")
    pdf_canvas.drawCentredString(11*72/2, 2.6*72, f"Instructor: {cert.course.instructor or 'SmartFarm'}")
    
    # Footer
    pdf_canvas.setFont("Helvetica", 9)
    pdf_canvas.setFillColor(colors.HexColor('#92400e'))
    
    # Left signature
    pdf_canvas.drawString(0.5*72, 1.2*72, "_________________")
    pdf_canvas.drawString(0.5*72, 0.8*72, "SmartFarm Director")
    
    # Center certificate code
    pdf_canvas.drawCentredString(11*72/2, 1.2*72, cert_code)
    pdf_canvas.drawCentredString(11*72/2, 0.8*72, "Certificate Code")
    
    # Right date
    date_str = cert.issued_at.strftime('%b %d, %Y')
    pdf_canvas.drawRightString(10.5*72, 1.2*72, date_str)
    pdf_canvas.drawRightString(10.5*72, 0.8*72, "Date Issued")
    
    # Save PDF
    pdf_canvas.save()
    
    # Get PDF from buffer
    pdf_buffer.seek(0)
    
    # Return PDF as download
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'SmartFarm_Certificate_{cert_code}.pdf'
    )