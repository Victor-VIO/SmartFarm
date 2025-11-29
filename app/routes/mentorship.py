from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, MentorshipRequest, Message
from datetime import datetime

mentorship_bp = Blueprint('mentorship', __name__, url_prefix='/mentorship')

@mentorship_bp.route('/browse')
def browse_mentors():
    """Browse available mentors"""
    page = request.args.get('page', 1, type=int)
    expertise = request.args.get('expertise', None)
    
    query = User.query.filter_by(role='mentor', is_active=True)
    
    if expertise:
        query = query.filter(User.expertise.contains(expertise))
    
    mentors = query.paginate(page=page, per_page=12)
    
    # Get unique expertise areas
    all_expertise = db.session.query(User.expertise).filter(User.role == 'mentor').distinct().all()
    expertise_list = [e[0] for e in all_expertise if e[0]]
    
    return render_template('mentorship/browse.html',
                         mentors=mentors,
                         expertise_list=expertise_list,
                         selected_expertise=expertise)

@mentorship_bp.route('/<int:mentor_id>')
def view_mentor(mentor_id):
    """View mentor profile"""
    mentor = User.query.filter_by(id=mentor_id, role='mentor').first_or_404()
    
    # Check if current user has pending/accepted request
    request_status = None
    if current_user.is_authenticated and current_user.id != mentor_id:
        existing_request = MentorshipRequest.query.filter_by(
            student_id=current_user.id,
            mentor_id=mentor_id
        ).first()
        if existing_request:
            request_status = existing_request.status
    
    return render_template('mentorship/profile.html',
                         mentor=mentor,
                         request_status=request_status)

@mentorship_bp.route('/request/<int:mentor_id>', methods=['POST'])
@login_required
def request_mentorship(mentor_id):
    """Send mentorship request"""
    if current_user.role != 'student':
        return jsonify({'error': 'Only students can request mentorship'}), 403
    
    mentor = User.query.filter_by(id=mentor_id, role='mentor').first()
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    
    # Check for existing request
    existing = MentorshipRequest.query.filter_by(
        student_id=current_user.id,
        mentor_id=mentor_id
    ).first()
    
    if existing:
        return jsonify({'error': f'You already have a {existing.status} request with this mentor'}), 400
    
    message = request.form.get('message', '')
    
    # Create mentorship request
    mentorship_req = MentorshipRequest(
        student_id=current_user.id,
        mentor_id=mentor_id,
        message=message,
        status='pending'
    )
    db.session.add(mentorship_req)
    db.session.commit()
    
    flash('Mentorship request sent successfully!', 'success')
    return redirect(url_for('mentorship.view_mentor', mentor_id=mentor_id))

@mentorship_bp.route('/requests')
@login_required
def my_requests():
    """View my mentorship requests (for students) or received requests (for mentors)"""
    if current_user.role == 'student':
        requests = MentorshipRequest.query.filter_by(student_id=current_user.id).all()
        template = 'mentorship/my_requests.html'
    elif current_user.role == 'mentor':
        requests = MentorshipRequest.query.filter_by(mentor_id=current_user.id).all()
        template = 'mentorship/received_requests.html'
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template(template, requests=requests)

@mentorship_bp.route('/request/<int:request_id>/respond', methods=['POST'])
@login_required
def respond_to_request(request_id):
    """Mentor responds to mentorship request"""
    mentorship_req = MentorshipRequest.query.get_or_404(request_id)
    
    if mentorship_req.mentor_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    action = request.form.get('action')  # 'accept' or 'reject'
    
    if action == 'accept':
        mentorship_req.status = 'accepted'
        flash('Mentorship request accepted!', 'success')
    elif action == 'reject':
        mentorship_req.status = 'rejected'
        flash('Mentorship request rejected.', 'info')
    
    mentorship_req.responded_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('mentorship.my_requests'))

@mentorship_bp.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    """Chat with mentor or student"""
    other_user = User.query.get_or_404(user_id)
    
    # Check if mentorship is accepted
    mentorship = MentorshipRequest.query.filter(
        (
            (MentorshipRequest.student_id == current_user.id) & 
            (MentorshipRequest.mentor_id == user_id)
        ) |
        (
            (MentorshipRequest.student_id == user_id) & 
            (MentorshipRequest.mentor_id == current_user.id)
        ),
        MentorshipRequest.status == 'accepted'
    ).first()
    
    if not mentorship:
        flash('You must have an accepted mentorship to chat.', 'warning')
        return redirect(url_for('mentorship.browse_mentors'))
    
    # Get conversation history (all messages between these two users)
    messages = Message.query.filter(
        (
            (Message.sender_id == current_user.id) & 
            (Message.recipient_id == user_id)
        ) |
        (
            (Message.sender_id == user_id) & 
            (Message.recipient_id == current_user.id)
        )
    ).order_by(Message.created_at).all()
    
    print(f"Chat between {current_user.id} and {user_id}")
    print(f"Found {len(messages)} messages")
    
    return render_template('mentorship/chat.html',
                         mentor=other_user,
                         messages=messages,
                         current_user_id=current_user.id)

@mentorship_bp.route('/message/<int:recipient_id>', methods=['POST'])
@login_required
def send_message(recipient_id):
    """Send message to mentor/student"""
    try:
        recipient = User.query.get_or_404(recipient_id)
        content = request.form.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Create message
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content
        )
        
        db.session.add(message)
        db.session.commit()
        
        print(f"Message saved: From {current_user.id} to {recipient_id}: {content}")
        
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'sender': current_user.username,
                'sender_id': current_user.id,
                'content': content,
                'created_at': message.created_at.strftime('%I:%M %p')
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error sending message: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500
