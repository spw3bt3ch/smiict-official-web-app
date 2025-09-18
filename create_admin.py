#!/usr/bin/env python3
"""
Script to create an admin user for the SMIICT Institute Course Platform
Run this script after setting up the database to create your first admin user.
ONLY affects admin users - preserves all courses and other data.
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Only delete existing admin users (preserve all other data)
        existing_admins = User.query.filter_by(role='admin').all()
        if existing_admins:
            print(f"Found {len(existing_admins)} existing admin users. Deleting...")
            for admin in existing_admins:
                print(f"  - Deleting admin: {admin.name} ({admin.email})")
                db.session.delete(admin)
            db.session.commit()
            print("✅ All existing admin users deleted")
        else:
            print("No existing admin users found")
        
        # Create new admin user
        admin = User(
            name='System Admin',
            email='admin@smiit.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            admin_approved=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ New admin user created successfully!")
        print("Email: admin@smiit.com")
        print("Password: admin123")
        print("Please change the password after first login!")
        
        # Verify what was preserved
        from models import Course, Application, ContactMessage
        course_count = Course.query.count()
        application_count = Application.query.count()
        contact_count = ContactMessage.query.count()
        
        print(f"\n�� Data preserved:")
        print(f"  - Courses: {course_count}")
        print(f"  - Applications: {application_count}")
        print(f"  - Contact Messages: {contact_count}")

if __name__ == '__main__':
    create_admin()