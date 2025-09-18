#!/usr/bin/env python3
"""
Script to create an admin user for the SMIICT Institute Course Platform
Run this script after setting up the database to create your first admin user.
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@smiit.com').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@smiit.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Email: admin@smiit.com")
        print("Password: admin123")
        print("Please change the password after first login!")

if __name__ == '__main__':
    create_admin()
