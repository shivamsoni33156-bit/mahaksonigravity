
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# Razorpay client will be initialized later when needed
RAZORPAY_KEY_ID = 'rzp_test_your_key_id_here'
RAZORPAY_KEY_SECRET = 'your_key_secret_here'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PDF_FOLDER'] = 'static/uploads/pdf'
app.config['ASSIGNMENT_FOLDER'] = 'static/uploads/assignments'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
os.makedirs(app.config['ASSIGNMENT_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'student_login'

# RAZORPAY - Replace with your keys (Client imported only when needed)
RAZORPAY_KEY_ID = 'rzp_test_your_key_id_here'
RAZORPAY_KEY_SECRET = 'your_key_secret_here'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(120))

class Student(User):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    phone = db.Column(db.String(20))

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(120))
    subject = db.Column(db.String(50))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    price = db.Column(db.Float)
    image = db.Column(db.String(200))

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)
    razorpay_payment_id = db.Column(db.String(100))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')

class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    course_id = db.Column(db.Integer)
    file_path = db.Column(db.String(200))
    teacher_id = db.Column(db.Integer)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    course_id = db.Column(db.Integer)
    file_path = db.Column(db.String(200))
    teacher_id = db.Column(db.Integer)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('DB created')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def courses():
    courses_list = Course.query.all()
    if not courses_list:
        # Seed sample courses
        sample_courses = [
            Course(name="IIT-JEE Preparation", description="Complete JEE Main & Advanced preparation with 500+ hours video lectures, notes & tests.", duration="2 Years", price=25000, image="https://images.unsplash.com/photo-1551671347-4b112245f6a9?w=400"),
            Course(name="NEET Preparation", description="Target NEET UG with expert Biology, Physics & Chemistry coaching.", duration="1 Year", price=18000, image="https://images.unsplash.com/photo-1576091160399-1d65c3098d8a?w=400"),
            Course(name="Class 11 Science", description="PCM/PCB for Class 11 - Foundation for competitive exams.", duration="1 Year", price=12000, image="https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400"),
            Course(name="Class 12 Science", description="Advanced Class 12 syllabus + JEE/NEET booster batches.", duration="1 Year", price=15000, image="https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=400"),
            Course(name="Foundation (Class 9-10)", description="Early preparation for competitive exams with Olympiad focus.", duration="2 Years", price=8000, image="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=400")
        ]
        for course in sample_courses:
            db.session.add(course)
        db.session.commit()
        courses_list = Course.query.all()
    return render_template('courses.html', courses=courses_list)

# Placeholder routes
@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('student_login.html')

@app.route('/student-signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('student_signup.html')
        
        user = User(username=username, email=email, password_hash=password)
        db.session.add(user)
        db.session.flush()  # Get ID
        
        student = Student(student_id=user.id, phone=phone)
        db.session.add(student)
        db.session.commit()
        
        flash('Account created! Please login.')
        return redirect(url_for('student_login'))
    
    return render_template('student_signup.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    payments = Payment.query.filter_by(student_id=current_user.id).all()
    return render_template('student_dashboard.html', payments=payments)

@app.route('/payment')
def payment():
    course_id = request.args.get('course_id')
    course = Course.query.get_or_404(course_id)
    return render_template('payment.html', course=course)

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    data = request.json
    # Simulate verification (real: use Razorpay API)
    payment = Payment(
        student_id=data['student_id'],
        course_id=data['course_id'],
        razorpay_payment_id=data['razorpay_payment_id'],
        amount=data.get('amount', 0),
        status='success'  # Sim successful
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/teacher-login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher and check_password_hash(teacher.password_hash, password):
            # Login teacher (extend LoginManager or use session)
            return redirect(url_for('teacher_dashboard'))
        flash('Invalid credentials')
    return render_template('teacher_login.html')

@app.route('/teacher-dashboard')
def teacher_dashboard():
    courses_list = Course.query.all()
    payments = Payment.query.join(Course).all()
    return render_template('teacher_dashboard.html', courses=courses_list, payments=payments)

@app.route('/upload-material', methods=['POST'])
def upload_material():
    course_id = request.form['course_id']
    title = request.form['title']
    file = request.files['pdf_file']
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['PDF_FOLDER'], filename)
        file.save(filepath)
        
        material = StudyMaterial(title=title, course_id=course_id, file_path=filepath, teacher_id=1)  # temp teacher_id
        db.session.add(material)
        db.session.commit()
        flash('Material uploaded successfully')
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/upload-assignment', methods=['POST'])
def upload_assignment():
    course_id = request.form['course_id']
    title = request.form['title']
    file = request.files['assignment_file']
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['ASSIGNMENT_FOLDER'], filename)
        file.save(filepath)
        
        assignment = Assignment(title=title, course_id=course_id, file_path=filepath, teacher_id=1)  # temp
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment uploaded successfully')
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'admin@gravity.com' and password == 'admin123':  # hardcoded for demo
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    students_count = User.query.count()
    teachers_count = Teacher.query.count()
    payments_success_count = Payment.query.filter_by(status='success').count()
    courses_count = Course.query.count()
    recent_payments = Payment.query.order_by(Payment.id.desc()).limit(10).all()
    return render_template('admin_dashboard.html', 
                         students_count=students_count,
                         teachers_count=teachers_count,
                         payments_success_count=payments_success_count,
                         courses_count=courses_count,
                         recent_payments=recent_payments)

@app.route('/admin-add-course', methods=['POST'])
def admin_add_course():
    course = Course(
        name=request.form['name'],
        description=request.form['description'],
        duration=request.form['duration'],
        price=float(request.form['price'])
    )
    db.session.add(course)
    db.session.commit()
    flash('Course added')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin-add-teacher', methods=['POST'])
def admin_add_teacher():
    teacher = Teacher(
        name=request.form['name'],
        email=request.form['email'],
        password_hash=generate_password_hash(request.form['password']),
        subject=request.form['subject']
    )
    db.session.add(teacher)
    db.session.commit()
    flash('Teacher added')
    return redirect(url_for('admin_dashboard'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = ContactMessage(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            message=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully! We will get back to you soon.')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# Add more routes later

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

