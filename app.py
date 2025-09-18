from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import logging
from config import Config
from utils.paystack_service import PaystackService
from utils.email_service import EmailService

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize extensions
login_manager = LoginManager()
mail = Mail()
email_service = None  # Will be initialized after mail is initialized

# Import models and db
from models import db, User, Course, Application, ContactMessage, Coupon, CouponUsage

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

# Initialize email service after mail is initialized
with app.app_context():
    email_service = EmailService(mail)

login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)

@app.route('/apply/<int:course_id>', methods=['GET', 'POST'])
@login_required
def apply_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        # Create application
        application = Application(
            user_id=current_user.id,
            course_id=course_id,
            status='pending',
            applied_at=datetime.utcnow(),
            original_price=course.price,
            discount_amount=0,
            final_price=course.price
        )
        db.session.add(application)
        db.session.commit()
        
        # Send course application email to user
        try:
            email_service.send_course_application_email(current_user, course, application)
            flash('Application submitted successfully! You will receive a confirmation email shortly.', 'success')
        except Exception as e:
            app.logger.error(f"Error sending course application email: {str(e)}")
            flash('Application submitted successfully!', 'success')
        
        # Send notification email to admin
        try:
            admin_users = User.query.filter_by(role='admin', admin_approved=True).all()
            for admin in admin_users:
                email_service.send_admin_notification_email(admin.email, current_user, course, application)
        except Exception as e:
            app.logger.error(f"Error sending admin notification email: {str(e)}")
        
        return redirect(url_for('payment', application_id=application.id))
    
    return render_template('apply_course.html', course=course)

@app.route('/payment/<int:application_id>')
@login_required
def payment(application_id):
    application = Application.query.get_or_404(application_id)
    if application.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    return render_template('payment.html', application=application)

@app.route('/payment/course/<int:course_id>')
@login_required
def payment_course(course_id):
    """Create application and redirect to payment for a specific course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user already has a pending application for this course
    existing_app = Application.query.filter_by(
        user_id=current_user.id, 
        course_id=course_id,
        payment_status='pending'
    ).first()
    
    if existing_app:
        return redirect(url_for('payment', application_id=existing_app.id))
    
    # Create new application
    application = Application(
        user_id=current_user.id,
        course_id=course_id,
        status='pending',
        applied_at=datetime.utcnow(),
        original_price=course.price,
        discount_amount=0,
        final_price=course.price
    )
    db.session.add(application)
    db.session.commit()
    
    return redirect(url_for('payment', application_id=application.id))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
            created_at=datetime.utcnow()
        )
        db.session.add(contact_msg)
        db.session.commit()
        
        # Send email notification
        try:
            email_service.send_contact_notification(contact_msg)
        except Exception as e:
            app.logger.error(f"Error sending contact notification email: {str(e)}")
        
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Check if admin user is approved
            if user.role == 'admin' and not user.admin_approved:
                flash('Your admin account is pending approval. Please contact a super admin.', 'warning')
                return render_template('login.html')
            
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'student')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            admin_approved=True if role != 'admin' else False  # Auto-approve non-admin roles
        )
        db.session.add(user)
        db.session.commit()
        
        if role == 'admin':
            flash('Admin registration submitted! Your account will be reviewed and approved by a super admin before you can log in.', 'info')
        else:
            flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # Send password reset email
            try:
                if email_service.send_password_reset_email(user, reset_token):
                    flash('Password reset link sent to your email address.', 'success')
                else:
                    # For debugging: show the reset link directly
                    reset_url = f"{app.config['BASE_URL']}/reset-password?token={reset_token}"
                    flash(f'Email service unavailable. Use this link to reset: {reset_url}', 'warning')
            except Exception as e:
                # Log the error for debugging
                print(f"Email sending error: {str(e)}")
                # For debugging: show the reset link directly
                reset_url = f"{app.config['BASE_URL']}/reset-password?token={reset_token}"
                flash(f'Email service temporarily unavailable. Use this link to reset: {reset_url}', 'warning')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        
        return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    
    if not token:
        flash('Invalid or missing reset token.', 'error')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.is_reset_token_valid(token):
        flash('Invalid or expired reset token. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('reset_password.html')
        
        # Update password
        user.password_hash = generate_password_hash(password)
        user.clear_reset_token()
        db.session.commit()
        
        flash('Your password has been reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    courses = Course.query.all()
    applications = Application.query.all()
    messages = ContactMessage.query.all()
    users = User.query.all()
    
    return render_template('admin/dashboard.html', 
                         courses=courses, 
                         applications=applications, 
                         messages=messages,
                         users=users)

@app.route('/admin/courses')
@login_required
def admin_courses():
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        duration = request.form['duration']
        price = float(request.form['price'])
        
        # Handle image upload
        image_url = None
        if 'course_image' in request.files:
            file = request.files['course_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f'/static/uploads/{filename}'
        
        course = Course(
            title=title,
            description=description,
            duration=duration,
            price=price,
            image_url=image_url
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/add_course.html')

@app.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        course.duration = request.form['duration']
        course.price = float(request.form['price'])
        
        # Handle image upload
        if 'course_image' in request.files:
            file = request.files['course_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                course.image_url = f'/static/uploads/{filename}'
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/edit_course.html', course=course)

@app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    course = Course.query.get_or_404(course_id)
    
    # Delete the image file if it exists
    if course.image_url and course.image_url.startswith('/static/uploads/'):
        image_path = course.image_url.replace('/static/uploads/', '')
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin_courses'))

@app.route('/admin/messages')
@login_required
def admin_messages():
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/<int:message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.role = request.form['role']
        
        # Only update password if provided
        if request.form['password']:
            user.password_hash = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    # Delete user's applications first
    Application.query.filter_by(user_id=user_id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        flash('You cannot change your own status.', 'error')
        return redirect(url_for('admin_users'))
    
    # Toggle user status (you can add an 'active' field to User model if needed)
    # For now, we'll just toggle the role between 'student' and 'inactive'
    if user.role == 'inactive':
        user.role = 'student'
        message = 'User activated successfully!'
    else:
        user.role = 'inactive'
        message = 'User deactivated successfully!'
    
    db.session.commit()
    flash(message, 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/pending-admins')
@login_required
def pending_admins():
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    pending_admins = User.query.filter_by(role='admin', admin_approved=False).order_by(User.created_at.desc()).all()
    return render_template('admin/pending_admins.html', pending_admins=pending_admins)

@app.route('/admin/approve-admin/<int:user_id>', methods=['POST'])
@login_required
def approve_admin(user_id):
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.role != 'admin':
        flash('User is not an admin.', 'error')
        return redirect(url_for('pending_admins'))
    
    user.admin_approved = True
    db.session.commit()
    
    flash(f'Admin {user.name} has been approved successfully!', 'success')
    return redirect(url_for('pending_admins'))

@app.route('/admin/reject-admin/<int:user_id>', methods=['POST'])
@login_required
def reject_admin(user_id):
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.role != 'admin':
        flash('User is not an admin.', 'error')
        return redirect(url_for('pending_admins'))
    
    # Change role to student and delete the user
    user.role = 'student'
    user.admin_approved = True  # Set to True so they can login as student
    db.session.commit()
    
    flash(f'Admin application for {user.name} has been rejected. User can now login as a student.', 'success')
    return redirect(url_for('pending_admins'))

# Coupon Management Routes
@app.route('/admin/coupons')
@login_required
def admin_coupons():
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin/coupons.html', coupons=coupons)

@app.route('/admin/coupons/create', methods=['GET', 'POST'])
@login_required
def create_coupon():
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        code = request.form.get('code').upper().strip()
        description = request.form.get('description')
        discount_type = request.form.get('discount_type')
        discount_value = float(request.form.get('discount_value'))
        min_amount = float(request.form.get('min_amount', 0))
        max_discount = request.form.get('max_discount')
        max_discount = float(max_discount) if max_discount else None
        usage_limit = request.form.get('usage_limit')
        usage_limit = int(usage_limit) if usage_limit else None
        user_limit = int(request.form.get('user_limit', 1))
        valid_until = request.form.get('valid_until')
        valid_until = datetime.strptime(valid_until, '%Y-%m-%dT%H:%M') if valid_until else None
        
        # Validate coupon code uniqueness
        existing_coupon = Coupon.query.filter_by(code=code).first()
        if existing_coupon:
            flash('Coupon code already exists. Please choose a different code.', 'error')
            return render_template('admin/create_coupon.html')
        
        # Validate discount values
        if discount_type == 'percentage' and (discount_value < 0 or discount_value > 100):
            flash('Percentage discount must be between 0 and 100.', 'error')
            return render_template('admin/create_coupon.html')
        
        if discount_type == 'fixed' and discount_value < 0:
            flash('Fixed discount must be a positive number.', 'error')
            return render_template('admin/create_coupon.html')
        
        # Create coupon
        coupon = Coupon(
            code=code,
            description=description,
            discount_type=discount_type,
            discount_value=discount_value,
            min_amount=min_amount,
            max_discount=max_discount,
            usage_limit=usage_limit,
            user_limit=user_limit,
            valid_until=valid_until,
            created_by=current_user.id
        )
        
        db.session.add(coupon)
        db.session.commit()
        
        flash(f'Coupon "{code}" created successfully!', 'success')
        return redirect(url_for('admin_coupons'))
    
    return render_template('admin/create_coupon.html')

@app.route('/admin/coupons/<int:coupon_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_coupon(coupon_id):
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    coupon = Coupon.query.get_or_404(coupon_id)
    
    if request.method == 'POST':
        coupon.description = request.form.get('description')
        coupon.discount_type = request.form.get('discount_type')
        coupon.discount_value = float(request.form.get('discount_value'))
        coupon.min_amount = float(request.form.get('min_amount', 0))
        max_discount = request.form.get('max_discount')
        coupon.max_discount = float(max_discount) if max_discount else None
        usage_limit = request.form.get('usage_limit')
        coupon.usage_limit = int(usage_limit) if usage_limit else None
        coupon.user_limit = int(request.form.get('user_limit', 1))
        valid_until = request.form.get('valid_until')
        coupon.valid_until = datetime.strptime(valid_until, '%Y-%m-%dT%H:%M') if valid_until else None
        coupon.is_active = 'is_active' in request.form
        
        # Validate discount values
        if coupon.discount_type == 'percentage' and (coupon.discount_value < 0 or coupon.discount_value > 100):
            flash('Percentage discount must be between 0 and 100.', 'error')
            return render_template('admin/edit_coupon.html', coupon=coupon)
        
        if coupon.discount_type == 'fixed' and coupon.discount_value < 0:
            flash('Fixed discount must be a positive number.', 'error')
            return render_template('admin/edit_coupon.html', coupon=coupon)
        
        db.session.commit()
        flash(f'Coupon "{coupon.code}" updated successfully!', 'success')
        return redirect(url_for('admin_coupons'))
    
    return render_template('admin/edit_coupon.html', coupon=coupon)

@app.route('/admin/coupons/<int:coupon_id>/delete', methods=['POST'])
@login_required
def delete_coupon(coupon_id):
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    coupon = Coupon.query.get_or_404(coupon_id)
    code = coupon.code
    db.session.delete(coupon)
    db.session.commit()
    
    flash(f'Coupon "{code}" deleted successfully!', 'success')
    return redirect(url_for('admin_coupons'))

@app.route('/admin/coupons/<int:coupon_id>/toggle', methods=['POST'])
@login_required
def toggle_coupon_status(coupon_id):
    if current_user.role != 'admin' or not current_user.admin_approved:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    coupon = Coupon.query.get_or_404(coupon_id)
    coupon.is_active = not coupon.is_active
    db.session.commit()
    
    status = 'activated' if coupon.is_active else 'deactivated'
    flash(f'Coupon "{coupon.code}" {status} successfully!', 'success')
    return redirect(url_for('admin_coupons'))

# Coupon Validation API
@app.route('/api/validate-coupon', methods=['POST'])
@login_required
def validate_coupon():
    """Validate and apply coupon code"""
    try:
        data = request.get_json()
        code = data.get('code', '').upper().strip()
        course_id = data.get('course_id')
        
        if not code or not course_id:
            return jsonify({'success': False, 'message': 'Coupon code and course ID are required'}), 400
        
        # Get course
        course = Course.query.get_or_404(course_id)
        
        # Find coupon
        coupon = Coupon.query.filter_by(code=code, is_active=True).first()
        if not coupon:
            return jsonify({'success': False, 'message': 'Invalid coupon code'}), 400
        
        # Check if coupon is still valid
        now = datetime.utcnow()
        if coupon.valid_until and coupon.valid_until < now:
            return jsonify({'success': False, 'message': 'Coupon has expired'}), 400
        
        if coupon.valid_from > now:
            return jsonify({'success': False, 'message': 'Coupon is not yet valid'}), 400
        
        # Check minimum amount
        if course.price < coupon.min_amount:
            return jsonify({'success': False, 'message': f'Minimum order amount of ₦{coupon.min_amount:,.2f} required'}), 400
        
        # Check usage limits
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return jsonify({'success': False, 'message': 'Coupon usage limit reached'}), 400
        
        # Check user usage limit
        user_usage_count = CouponUsage.query.filter_by(coupon_id=coupon.id, user_id=current_user.id).count()
        if user_usage_count >= coupon.user_limit:
            return jsonify({'success': False, 'message': 'You have already used this coupon'}), 400
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount_amount = (course.price * coupon.discount_value) / 100
            if coupon.max_discount:
                discount_amount = min(discount_amount, coupon.max_discount)
        else:  # fixed
            discount_amount = min(coupon.discount_value, course.price)
        
        final_price = course.price - discount_amount
        
        return jsonify({
            'success': True,
            'coupon': {
                'id': coupon.id,
                'code': coupon.code,
                'description': coupon.description,
                'discount_type': coupon.discount_type,
                'discount_value': coupon.discount_value,
                'discount_amount': discount_amount,
                'original_price': course.price,
                'final_price': final_price
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error validating coupon: {str(e)}")
        return jsonify({'success': False, 'message': 'Error validating coupon'}), 500

# Paystack Payment Routes
@app.route('/payment/initialize', methods=['POST'])
@login_required
def initialize_payment():
    """Initialize Paystack payment"""
    try:
        application_id = request.form.get('application_id')
        if not application_id:
            return jsonify({'success': False, 'message': 'Application ID is required'}), 400
        
        application = Application.query.get_or_404(application_id)
        
        # Check if user owns this application
        if application.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Check if payment is already completed
        if application.payment_status == 'completed':
            return jsonify({'success': False, 'message': 'Payment already completed'}), 400
        
        # Handle coupon code if provided
        coupon_code = request.form.get('coupon_code', '').upper().strip()
        coupon = None
        discount_amount = 0
        final_price = application.course.price
        
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
            if coupon:
                # Validate coupon
                now = datetime.utcnow()
                if (coupon.valid_until and coupon.valid_until < now) or coupon.valid_from > now:
                    return jsonify({'success': False, 'message': 'Coupon has expired or is not yet valid'}), 400
                
                if application.course.price < coupon.min_amount:
                    return jsonify({'success': False, 'message': f'Minimum order amount of ₦{coupon.min_amount:,.2f} required'}), 400
                
                if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                    return jsonify({'success': False, 'message': 'Coupon usage limit reached'}), 400
                
                user_usage_count = CouponUsage.query.filter_by(coupon_id=coupon.id, user_id=current_user.id).count()
                if user_usage_count >= coupon.user_limit:
                    return jsonify({'success': False, 'message': 'You have already used this coupon'}), 400
                
                # Calculate discount
                if coupon.discount_type == 'percentage':
                    discount_amount = (application.course.price * coupon.discount_value) / 100
                    if coupon.max_discount:
                        discount_amount = min(discount_amount, coupon.max_discount)
                else:  # fixed
                    discount_amount = min(coupon.discount_value, application.course.price)
                
                final_price = application.course.price - discount_amount
            else:
                return jsonify({'success': False, 'message': 'Invalid coupon code'}), 400
        
        # Update application with pricing info
        application.original_price = application.course.price
        application.discount_amount = discount_amount
        application.final_price = final_price
        if coupon:
            application.coupon_id = coupon.id
        db.session.commit()
        
        # Generate unique reference
        reference = f"PAY_{uuid.uuid4().hex[:10].upper()}"
        
        # Initialize Paystack service
        paystack_service = PaystackService()
        
        # Prepare metadata
        metadata = {
            'application_id': application.id,
            'course_id': application.course_id,
            'user_id': current_user.id,
            'course_title': application.course.title
        }
        
        # Initialize transaction
        result = paystack_service.initialize_transaction(
            email=current_user.email,
            amount=final_price,
            reference=reference,
            metadata=metadata
        )
        
        if result['success']:
            # Update application with payment reference
            application.payment_reference = reference
            application.payment_status = 'pending'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'authorization_url': result['data']['authorization_url'],
                'reference': reference
            })
        else:
            return jsonify({'success': False, 'message': result['message']}), 400
            
    except Exception as e:
        app.logger.error(f"Error initializing payment: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@app.route('/payment/verify/<reference>')
@login_required
def verify_payment(reference):
    """Verify Paystack payment"""
    try:
        # Find application by payment reference
        application = Application.query.filter_by(payment_reference=reference).first()
        if not application:
            flash('Payment reference not found.', 'error')
            return redirect(url_for('index'))
        
        # Check if user owns this application
        if application.user_id != current_user.id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('index'))
        
        # Initialize Paystack service
        paystack_service = PaystackService()
        
        # Verify transaction
        result = paystack_service.verify_transaction(reference)
        
        if result['success']:
            # Update application status
            application.payment_status = 'completed'
            application.paid_at = datetime.utcnow()
            
            # Record coupon usage if applicable
            if application.coupon_id:
                coupon = Coupon.query.get(application.coupon_id)
                if coupon:
                    # Update coupon usage count
                    coupon.used_count += 1
                    
                    # Create coupon usage record
                    coupon_usage = CouponUsage(
                        coupon_id=coupon.id,
                        user_id=application.user_id,
                        application_id=application.id,
                        discount_amount=application.discount_amount
                    )
                    db.session.add(coupon_usage)
            
            db.session.commit()
            
            # Send payment confirmation email
            try:
                user = User.query.get(application.user_id)
                course = Course.query.get(application.course_id)
                email_service.send_payment_confirmation_email(user, course, application)
            except Exception as e:
                app.logger.error(f"Error sending payment confirmation email: {str(e)}")
            
            flash('Payment successful! Your application has been submitted. You will receive a confirmation email shortly.', 'success')
            return redirect(url_for('course_detail', course_id=application.course_id))
        else:
            application.payment_status = 'failed'
            db.session.commit()
            
            flash('Payment verification failed. Please try again.', 'error')
            return redirect(url_for('payment', application_id=application.id))
            
    except Exception as e:
        app.logger.error(f"Error verifying payment: {str(e)}")
        flash('An error occurred during payment verification.', 'error')
        return redirect(url_for('index'))

@app.route('/payment/callback')
def payment_callback():
    """Handle Paystack callback"""
    try:
        reference = request.args.get('reference')
        if not reference:
            return jsonify({'success': False, 'message': 'Reference not provided'}), 400
        
        # Find application by payment reference
        application = Application.query.filter_by(payment_reference=reference).first()
        if not application:
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        # Initialize Paystack service
        paystack_service = PaystackService()
        
        # Verify transaction
        result = paystack_service.verify_transaction(reference)
        
        if result['success']:
            # Update application status
            application.payment_status = 'completed'
            application.paid_at = datetime.utcnow()
            db.session.commit()
            
            # Send payment confirmation email
            try:
                user = User.query.get(application.user_id)
                course = Course.query.get(application.course_id)
                email_service.send_payment_confirmation_email(user, course, application)
            except Exception as e:
                app.logger.error(f"Error sending payment confirmation email: {str(e)}")
            
            return jsonify({'success': True, 'message': 'Payment verified successfully'})
        else:
            application.payment_status = 'failed'
            db.session.commit()
            
            return jsonify({'success': False, 'message': 'Payment verification failed'})
            
    except Exception as e:
        app.logger.error(f"Error in payment callback: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
