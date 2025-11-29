from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

# ============ USER MODEL ============
class User(UserMixin, db.Model):
    """User model for students, mentors, and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(255), default='default.png')
    bio = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(20), default='student')  # 'student', 'mentor', 'admin'
    expertise = db.Column(db.String(255), nullable=True)  # For mentors: farming techniques, etc.
    is_active = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(10), default='light')  # 'light' or 'dark'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses_enrolled = db.relationship('CourseEnrollment', backref='student', lazy=True, foreign_keys='CourseEnrollment.student_id')
    mentorship_requests_sent = db.relationship('MentorshipRequest', backref='requester', lazy=True, foreign_keys='MentorshipRequest.student_id')
    mentorship_requests_received = db.relationship('MentorshipRequest', backref='mentor', lazy=True, foreign_keys='MentorshipRequest.mentor_id')
    messages_sent = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# ============ COURSE MODEL ============
class Course(db.Model):
    """Course model for agriculture training"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # e.g., 'crop farming', 'animal husbandry'
    level = db.Column(db.String(20), default='beginner')  # 'beginner', 'intermediate', 'advanced'
    duration_weeks = db.Column(db.Integer, default=4)
    instructor = db.Column(db.String(120), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)  # YouTube, Vimeo link
    thumbnail = db.Column(db.String(255), default='course-default.png')
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    modules = db.relationship('CourseModule', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'

# ============ COURSE MODULE MODEL ============
class CourseModule(db.Model):
    """Individual modules/lessons within a course"""
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=1)
    video_url = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)
    quiz_questions = db.Column(db.Text, nullable=True)  # JSON format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourseModule {self.title}>'

# ============ COURSE ENROLLMENT MODEL ============
class CourseEnrollment(db.Model):
    """Track which students are enrolled in which courses"""
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    modules_completed = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    certificate_earned = db.Column(db.Boolean, default=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<CourseEnrollment student={self.student_id} course={self.course_id}>'

# ============ MENTORSHIP REQUEST MODEL ============
class MentorshipRequest(db.Model):
    """Handle mentorship requests from students to mentors"""
    __tablename__ = 'mentorship_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<MentorshipRequest student={self.student_id} mentor={self.mentor_id} status={self.status}>'

# ============ MESSAGE MODEL ============
class Message(db.Model):
    """Messages between student and mentor"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message from={self.sender_id} to={self.recipient_id}>'

# ============ CERTIFICATION MODEL ============
class Certificate(db.Model):
    """Digital certificates for completed courses"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    certificate_code = db.Column(db.String(50), unique=True, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', backref='certificates')
    course = db.relationship('Course', backref='certificates')
    
    def __repr__(self):
        return f'<Certificate student={self.student_id} course={self.course_id}>'