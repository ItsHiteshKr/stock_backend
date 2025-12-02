"""
Database connection and table verification script
"""
from sqlalchemy import inspect, text
from db.database import engine, SessionLocal
import sys

def check_connection():
    """Test basic database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_tables():
    """List all tables in the database"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"\n✓ Found {len(tables)} table(s) in database:")
            for table in tables:
                print(f"  - {table}")
                # Get columns for each table
                columns = inspector.get_columns(table)
                for col in columns:
                    print(f"    • {col['name']} ({col['type']})")
        else:
            print("\n⚠ No tables found in database.")
            print("Run init_db() to create tables from your models.")
        
        return tables
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        return []

def check_database_info():
    """Get database server information"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"\n✓ MySQL Version: {version}")
            
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.scalar()
            print(f"✓ Current Database: {db_name}")
    except Exception as e:
        print(f"✗ Error getting database info: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CONNECTION CHECK")
    print("=" * 60)
    
    # Check connection
    if not check_connection():
        sys.exit(1)
    
    # Get database info
    check_database_info()
    
    # Check tables
    tables = check_tables()
    
    print("\n" + "=" * 60)
    if not tables:
        print("\nNEXT STEPS:")
        print("1. Make sure your models are defined")
        print("2. Run: python -c \"from db.batabase import init_db; init_db()\"")
        print("   OR create an init_db.py script")
    else:
        print("\n✓ Database is ready to use!")
    print("=" * 60)
