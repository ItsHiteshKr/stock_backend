"""
Initialize database tables from models
"""
from db.batabase import init_db, Base, engine
from sqlalchemy import inspect

# Import all models so they're registered with Base
from model.user_model import UserTable
from model.nifty_model import NiftyTable

def main():
    print("=" * 60)
    print("INITIALIZING DATABASE TABLES")
    print("=" * 60)
    
    # Show which models will be created
    print("\nModels to create:")
    for mapper in Base.registry.mappers:
        print(f"  - {mapper.class_.__tablename__} ({mapper.class_.__name__})")
    
    # Create all tables
    print("\nCreating tables...")
    try:
        init_db()
        print("✓ Tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return
    
    # Verify tables were created
    print("\nVerifying tables in database:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n✓ Table: {table}")
        print("  Columns:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"    • {col['name']:<20} {str(col['type']):<20} {nullable}")
    
    print("\n" + "=" * 60)
    print("✓ DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
