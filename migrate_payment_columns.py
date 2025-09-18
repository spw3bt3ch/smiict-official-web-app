#!/usr/bin/env python3
"""
Database Migration Script
Adds payment-related columns to the application table
"""

from app import app, db
from sqlalchemy import text

def migrate_payment_columns():
    """Add payment columns to application table"""
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'application' 
                AND column_name IN ('payment_reference', 'paid_at')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'payment_reference' not in existing_columns:
                print("Adding payment_reference column...")
                db.session.execute(text("""
                    ALTER TABLE application 
                    ADD COLUMN payment_reference VARCHAR(100) UNIQUE
                """))
                print("✅ payment_reference column added")
            else:
                print("✅ payment_reference column already exists")
            
            if 'paid_at' not in existing_columns:
                print("Adding paid_at column...")
                db.session.execute(text("""
                    ALTER TABLE application 
                    ADD COLUMN paid_at TIMESTAMP WITHOUT TIME ZONE
                """))
                print("✅ paid_at column added")
            else:
                print("✅ paid_at column already exists")
            
            # Update payment_status column if it doesn't have the right values
            print("Updating payment_status column...")
            db.session.execute(text("""
                UPDATE application 
                SET payment_status = 'pending' 
                WHERE payment_status IS NULL
            """))
            print("✅ payment_status column updated")
            
            # Commit all changes
            db.session.commit()
            print("🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_payment_columns()
