#!/usr/bin/env python3
"""
Run script for the SMIICT Institute Course Platform
This script initializes the database and starts the Flask application.
"""

from app import app, db
from models import User, Course, Application, ContactMessage

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

def create_sample_course():
    """Create a sample course for demonstration"""
    with app.app_context():
        # Check if sample course already exists
        existing_course = Course.query.filter_by(title='Web Development Fundamentals').first()
        if existing_course:
            print("Sample course already exists!")
            return
        
        sample_course = Course(
            title='Web Development Fundamentals',
            description='Learn the basics of web development including HTML, CSS, and JavaScript. This comprehensive course covers everything from basic markup to responsive design and interactive web applications. Perfect for beginners who want to start their journey in web development.',
            duration='3 months',
            price=299.99,
            image_url='https://images.unsplash.com/photo-1461749280684-dccba630e2f6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
        )
        
        db.session.add(sample_course)
        db.session.commit()
        print("Sample course created successfully!")

if __name__ == '__main__':
    print("Starting SMIICT Institute Course Platform...")
    print("Initializing database...")
    init_database()
    
    print("Creating sample course...")
    create_sample_course()
    
    print("Starting Flask application...")
    print("Visit http://localhost:5000 to access the platform")
    print("Admin panel: http://localhost:5000/admin")
    print("Contact page: http://localhost:5000/contact")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
