from app import create_app, db
from app.models import User, Course, CourseModule, CourseEnrollment

app = create_app()

with app.app_context():
    # Clear existing data
    print("Clearing database...")
    db.drop_all()
    db.create_all()
    
    # Create admin user
    print("Creating admin user...")
    admin = User(
        username='admin',
        email='admin@smartfarm.com',
        full_name='Admin User',
        role='admin'
    )
    admin.set_password('Admin123456')
    db.session.add(admin)
    
    # Create mentor users
    print("Creating mentors...")
    mentor1 = User(
        username='mentor_john',
        email='john@smartfarm.com',
        full_name='John Kimani',
        role='mentor',
        expertise='Crop Farming - Maize & Beans',
        bio='10+ years experience in sustainable crop farming. Passionate about helping young farmers succeed.'
    )
    mentor1.set_password('Mentor123456')
    db.session.add(mentor1)
    
    mentor2 = User(
        username='mentor_jane',
        email='jane@smartfarm.com',
        full_name='Jane Ochieng',
        role='mentor',
        expertise='Dairy Farming & Animal Husbandry',
        bio='Certified dairy farmer with expertise in modern livestock management and profitability.'
    )
    mentor2.set_password('Mentor123456')
    db.session.add(mentor2)
    
    # Create student users
    print("Creating students...")
    student1 = User(
        username='student_alice',
        email='alice@smartfarm.com',
        full_name='Alice Kipchoge',
        role='student',
        bio='Passionate about modern agriculture'
    )
    student1.set_password('Student123456')
    db.session.add(student1)
    
    student2 = User(
        username='student_bob',
        email='bob@smartfarm.com',
        full_name='Bob Mutua',
        role='student'
    )
    student2.set_password('Student123456')
    db.session.add(student2)
    
    db.session.commit()
    
    # Create courses
    print("Creating courses...")
    course1 = Course(
        title='Introduction to Crop Farming',
        description='Learn the fundamentals of modern crop farming including soil preparation, planting, and harvesting techniques.',
        category='Crop Farming',
        level='beginner',
        duration_weeks=4,
        instructor='John Kimani',
        is_published=True
    )
    db.session.add(course1)
    
    course2 = Course(
        title='Sustainable Dairy Farming Practices',
        description='Master dairy farming from breed selection to milk production and quality management.',
        category='Animal Husbandry',
        level='intermediate',
        duration_weeks=6,
        instructor='Jane Ochieng',
        is_published=True
    )
    db.session.add(course2)
    
    course3 = Course(
        title='Organic Vegetable Gardening',
        description='Growing nutritious vegetables using organic methods. Perfect for small-scale farmers.',
        category='Crop Farming',
        level='beginner',
        duration_weeks=3,
        instructor='John Kimani',
        is_published=True
    )
    db.session.add(course3)
    
    db.session.commit()
    
    # Create course modules
    print("Creating course modules...")
    for i, course in enumerate([course1, course2, course3], 1):
        for j in range(1, 4):  # 3 modules per course
            module = CourseModule(
                course_id=course.id,
                title=f'{course.title} - Module {j}',
                description=f'Learn about module {j} content',
                order=j,
                content=f'This is the content for module {j} of {course.title}.'
            )
            db.session.add(module)
    
    db.session.commit()
    
    # Create sample enrollment
    print("Creating sample enrollment...")
    enrollment = CourseEnrollment(
        student_id=student1.id,
        course_id=course1.id,
        progress_percentage=50.0,
        modules_completed=1
    )
    db.session.add(enrollment)
    db.session.commit()
    
    print("✅ Database seeded successfully!")
    print("\n📝 Test Credentials:")
    print("Admin: username='admin', password='Admin123456'")
    print("Mentor: username='mentor_john', password='Mentor123456'")
    print("Student: username='student_alice', password='Student123456'")