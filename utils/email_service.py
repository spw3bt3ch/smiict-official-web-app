"""
Email Service for SMIICT Institute Course Platform
Handles sending various types of emails to users
"""

from flask import render_template, current_app, url_for
from flask_mail import Message, Mail
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, mail):
        self.mail = mail
        self.base_url = current_app.config.get('BASE_URL', 'http://127.0.0.1:5000')
        self.sender_email = current_app.config.get('MAIL_USERNAME', 'noreply@smiict.com')
    
    def send_course_application_email(self, user, course, application):
        """
        Send course application confirmation email to user
        
        Args:
            user: User object
            course: Course object
            application: Application object
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Prepare email data
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            email_data = {
                'user_name': user.name,
                'user_email': user.email,
                'course': course,
                'application_date': application.applied_at.strftime('%B %d, %Y at %I:%M %p'),
                'application_status': application.status.title(),
                'contact_email': current_app.config['CONTACT_EMAIL'],
                'contact_phone': current_app.config['CONTACT_PHONE'],
                'website_url': f"{base_url}/",
                'course_url': f"{base_url}/course/{course.id}",
                'dashboard_url': f"{base_url}/"  # You can add a user dashboard later
            }
            
            # Create message
            msg = Message(
                subject=f"Course Application Confirmation - {course.title} | SMIICT Institute",
                recipients=[user.email],
                sender=current_app.config['MAIL_USERNAME']
            )
            
            # Set HTML and text content
            msg.html = render_template('emails/course_application.html', **email_data)
            msg.body = render_template('emails/course_application.txt', **email_data)
            
            # Send email
            self.mail.send(msg)
            
            logger.info(f"Course application email sent successfully to {user.email} for course {course.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending course application email to {user.email}: {str(e)}")
            return False
    
    def send_payment_confirmation_email(self, user, course, application):
        """
        Send payment confirmation email to user
        
        Args:
            user: User object
            course: Course object
            application: Application object
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Prepare email data
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            email_data = {
                'user_name': user.name,
                'user_email': user.email,
                'course': course,
                'payment_date': application.paid_at.strftime('%B %d, %Y at %I:%M %p') if application.paid_at else 'N/A',
                'payment_reference': application.payment_reference,
                'contact_email': current_app.config['CONTACT_EMAIL'],
                'contact_phone': current_app.config['CONTACT_PHONE'],
                'website_url': f"{base_url}/",
                'course_url': f"{base_url}/course/{course.id}"
            }
            
            # Create message
            msg = Message(
                subject=f"Payment Confirmation - {course.title} | SMIICT Institute",
                recipients=[user.email],
                sender=current_app.config['MAIL_USERNAME']
            )
            
            # Simple payment confirmation message
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Payment Confirmation - SMIICT Institute</h2>
                    
                    <p>Dear {user.name},</p>
                    
                    <p>Your payment for <strong>{course.title}</strong> has been successfully processed!</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3>Payment Details:</h3>
                        <p><strong>Course:</strong> {course.title}</p>
                        <p><strong>Amount:</strong> ₦{course.price:,}</p>
                        <p><strong>Payment Date:</strong> {email_data['payment_date']}</p>
                        <p><strong>Reference:</strong> {email_data['payment_reference']}</p>
                    </div>
                    
                    <p>You will receive your course materials and further instructions shortly.</p>
                    
                    <p>If you have any questions, please contact us at {email_data['contact_email']} or {email_data['contact_phone']}.</p>
                    
                    <p>Best regards,<br>The SMIICT Institute Team</p>
                </div>
            </body>
            </html>
            """
            
            msg.body = f"""
Payment Confirmation - SMIICT Institute

Dear {user.name},

Your payment for {course.title} has been successfully processed!

Payment Details:
- Course: {course.title}
- Amount: ₦{course.price:,}
- Payment Date: {email_data['payment_date']}
- Reference: {email_data['payment_reference']}

You will receive your course materials and further instructions shortly.

If you have any questions, please contact us at {email_data['contact_email']} or {email_data['contact_phone']}.

Best regards,
The SMIICT Institute Team
            """
            
            # Send email
            self.mail.send(msg)
            
            logger.info(f"Payment confirmation email sent successfully to {user.email} for course {course.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation email to {user.email}: {str(e)}")
            return False

    def send_admin_notification_email(self, admin_email, user, course, application):
        """
        Send notification email to admin about new course application
        
        Args:
            admin_email: Admin email address
            user: User object
            course: Course object
            application: Application object
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = Message(
                subject=f"New Course Application - {course.title} | SMIICT Institute Admin",
                recipients=[admin_email],
                sender=current_app.config['MAIL_USERNAME']
            )
            
            # Simple admin notification message
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">New Course Application - SMIICT Institute Admin</h2>
                    
                    <p>A new course application has been submitted:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3>Application Details:</h3>
                        <p><strong>Student:</strong> {user.name} ({user.email})</p>
                        <p><strong>Course:</strong> {course.title}</p>
                        <p><strong>Application Date:</strong> {application.applied_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Status:</strong> {application.status.title()}</p>
                        <p><strong>Payment Status:</strong> {application.payment_status.title() if application.payment_status else 'Not Started'}</p>
                    </div>
                    
                    <p>Please review the application in the admin dashboard.</p>
                    
                    <p>Best regards,<br>SMIICT Institute System</p>
                </div>
            </body>
            </html>
            """
            
            msg.body = f"""
New Course Application - SMIICT Institute Admin

A new course application has been submitted:

Application Details:
- Student: {user.name} ({user.email})
- Course: {course.title}
- Application Date: {application.applied_at.strftime('%B %d, %Y at %I:%M %p')}
- Status: {application.status.title()}
- Payment Status: {application.payment_status.title() if application.payment_status else 'Not Started'}

Please review the application in the admin dashboard.

Best regards,
SMIICT Institute System
            """
            
            # Send email
            self.mail.send(msg)
            
            logger.info(f"Admin notification email sent successfully to {admin_email} for application {application.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending admin notification email to {admin_email}: {str(e)}")
            return False
    
    def send_contact_notification(self, contact_message):
        """
        Send contact form notification email to admin
        
        Args:
            contact_message: ContactMessage object
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Get admin emails
            admin_emails = current_app.config.get('ADMIN_EMAILS', [current_app.config['MAIL_USERNAME']])
            
            # Create message
            msg = Message(
                subject=f"New Contact Form Submission - {contact_message.subject} | SMIICT Institute",
                recipients=admin_emails,
                sender=current_app.config['MAIL_USERNAME']
            )
            
            # Contact notification message
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">New Contact Form Submission - SMIICT Institute</h2>
                    
                    <p>A new message has been received through the contact form:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3>Contact Details:</h3>
                        <p><strong>Name:</strong> {contact_message.name}</p>
                        <p><strong>Email:</strong> {contact_message.email}</p>
                        <p><strong>Subject:</strong> {contact_message.subject}</p>
                        <p><strong>Date:</strong> {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 5px; border-left: 4px solid #007bff;">
                        <h3>Message:</h3>
                        <p style="white-space: pre-wrap;">{contact_message.message}</p>
                    </div>
                    
                    <p>Please respond to the customer at: {contact_message.email}</p>
                    
                    <p>Best regards,<br>SMIICT Institute System</p>
                </div>
            </body>
            </html>
            """
            
            msg.body = f"""
New Contact Form Submission - SMIICT Institute

A new message has been received through the contact form:

Contact Details:
- Name: {contact_message.name}
- Email: {contact_message.email}
- Subject: {contact_message.subject}
- Date: {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}

Message:
{contact_message.message}

Please respond to the customer at: {contact_message.email}

Best regards,
SMIICT Institute System
            """
            
            # Send email
            self.mail.send(msg)
            
            logger.info(f"Contact notification email sent successfully for message from {contact_message.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending contact notification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, user, reset_token):
        """
        Send password reset email to user
        """
        try:
            reset_url = f"{self.base_url}/reset-password?token={reset_token}"
            
            msg = Message(
                subject=f"Password Reset Request - SMIICT Institute",
                recipients=[user.email],
                sender=self.sender_email
            )
            
            # HTML version
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset Request - SMIICT Institute</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .button:hover {{ background: #45a049; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                        <p>SMIICT Institute - Professional IT Training and Certification</p>
                    </div>
                    <div class="content">
                        <h2 style="color: #2c3e50;">Hello {user.name},</h2>
                        <p>We received a request to reset your password for your SMIICT Institute account.</p>
                        <p>If you made this request, click the button below to reset your password:</p>
                        <div style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset My Password</a>
                        </div>
                        <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
                        <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                        <p><strong>If the button doesn't work, copy and paste this link into your browser:</strong></p>
                        <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 5px; font-family: monospace;">{reset_url}</p>
                        <p>Best regards,<br>The SMIICT Institute Team</p>
                    </div>
                    <div class="footer">
                        <p><strong>SMIICT Institute - Professional IT Training and Certification</strong></p>
                        <p>© 2024 SMIICT Institute. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            msg.body = f"""
SMIICT Institute - Professional IT Training and Certification

Hello {user.name},

We received a request to reset your password for your SMIICT Institute account.

If you made this request, click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

Best regards,
The SMIICT Institute Team

SMIICT Institute - Professional IT Training and Certification
© 2024 SMIICT Institute. All rights reserved.
            """
            
            # Send email
            self.mail.send(msg)
            
            logger.info(f"Password reset email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False