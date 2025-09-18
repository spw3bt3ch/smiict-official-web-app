from app import app, db
from sqlalchemy import text

def migrate_admin_approval():
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        try:
            # Add admin_approved column
            print("Adding admin_approval column...")
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN admin_approved BOOLEAN DEFAULT FALSE"))
            print("✅ admin_approval column added")
            
            # Set existing admins as approved
            print("Setting existing admins as approved...")
            conn.execute(text("UPDATE \"user\" SET admin_approved = TRUE WHERE role = 'admin'"))
            print("✅ Existing admins set as approved")
            
            trans.commit()
            print("🎉 Migration completed successfully!")
        except Exception as e:
            trans.rollback()
            print(f"❌ Migration failed: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_admin_approval()
