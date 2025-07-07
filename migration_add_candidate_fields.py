#!/usr/bin/env python3
"""
Database migration script to add new candidate fields to resumes table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.models.database import engine, SessionLocal

def run_migration():
    """Add new candidate fields to resumes table"""
    
    migration_sql = """
    -- Add new candidate fields to resumes table
    ALTER TABLE resumes 
    ADD COLUMN IF NOT EXISTS candidate_first_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS candidate_last_name VARCHAR(155),
    ADD COLUMN IF NOT EXISTS candidate_location VARCHAR(255),
    ADD COLUMN IF NOT EXISTS current_ctc VARCHAR(100),
    ADD COLUMN IF NOT EXISTS notice_period VARCHAR(100),
    ADD COLUMN IF NOT EXISTS total_experience VARCHAR(100);
    """
    
    try:
        with engine.connect() as connection:
            # Execute migration
            connection.execute(text(migration_sql))
            connection.commit()
            print("✅ Migration completed successfully!")
            print("Added new fields:")
            print("  - candidate_first_name")
            print("  - candidate_last_name") 
            print("  - candidate_location")
            print("  - current_ctc")
            print("  - notice_period")
            print("  - total_experience")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

def verify_migration():
    """Verify that the migration was successful"""
    try:
        with engine.connect() as connection:
            # Check if new columns exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'resumes' 
                AND column_name IN (
                    'candidate_first_name', 
                    'candidate_last_name', 
                    'candidate_location', 
                    'current_ctc', 
                    'notice_period', 
                    'total_experience'
                )
                ORDER BY column_name;
            """))
            
            columns = [row[0] for row in result.fetchall()]
            expected_columns = [
                'candidate_first_name',
                'candidate_last_name', 
                'candidate_location',
                'current_ctc',
                'notice_period',
                'total_experience'
            ]
            
            missing_columns = set(expected_columns) - set(columns)
            
            if missing_columns:
                print(f"❌ Migration verification failed. Missing columns: {missing_columns}")
                return False
            else:
                print("✅ Migration verification successful! All new columns are present.")
                return True
                
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("Adding new candidate fields to resumes table...")
    
    if run_migration():
        print("\n🔍 Verifying migration...")
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
        else:
            print("\n⚠️  Migration completed but verification failed.")
            sys.exit(1)
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)