# SMIICT Institute Course Platform

A professional Flask-based e-commerce website for course applications with admin panel and email notifications.

## Features

- **Course Management**: Add, view, and manage courses with images, descriptions, duration, and pricing
- **User Authentication**: Registration and login system for students and staff
- **Course Applications**: Students can apply for courses and proceed to payment
- **Admin Panel**: Complete admin dashboard for managing courses, applications, and messages
- **Contact System**: Contact form with email notifications
- **Email Notifications**: SMTP integration for receiving notifications
- **Professional UI**: Modern design with Tailwind CSS

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=a8b074350d022ac1d9e5672ce240a1afc7df44973ff08
```

### 3. Database Configuration

The database configuration is already set up in `config.py` with your PostgreSQL credentials:
- Host: smiit-smiict-63e0.e.aivencloud.com
- Port: 14156
- Database: defaultdb
- User: avnadmin

### 4. Email Configuration

Email settings are configured in `config.py`:
- SMTP Server: smtp.gmail.com
- Port: 587
- Username: samueloluwapelumi8@gmail.com
- Password: zgwv xctm atos lxzj

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### For Students
1. Register an account
2. Browse available courses
3. Click on a course to view details
4. Apply for the course
5. Complete payment

### For Admin
1. Register with admin role (you'll need to manually set this in the database)
2. Access admin dashboard at `/admin`
3. Add new courses
4. View applications and messages
5. Manage the platform

## Database Schema

- **Users**: Store user information and roles
- **Courses**: Store course details (title, description, duration, price, image)
- **Applications**: Track course applications and payment status
- **ContactMessages**: Store contact form submissions

## File Structure

```
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── utils/
│   └── email_service.py  # Email notification functions
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── course_detail.html # Course details page
    ├── apply_course.html # Course application page
    ├── payment.html      # Payment page
    ├── contact.html      # Contact page
    ├── login.html        # Login page
    ├── register.html     # Registration page
    └── admin/
        ├── dashboard.html # Admin dashboard
        ├── courses.html   # Course management
        ├── add_course.html # Add new course
        └── messages.html  # Message management
```

## Contact Information

- Email: samueloluwapelumi8@gmail.com
- Phone: 07077705842

## Security Notes

- Change the default secret key in production
- Use environment variables for sensitive data
- Implement proper password hashing (already included)
- Add CSRF protection for forms
- Set up SSL/HTTPS for production

## Future Enhancements

- Payment gateway integration (Stripe, PayPal)
- Course progress tracking
- Certificate generation
- Email templates
- File upload for course images
- Advanced admin features
- User profile management
