#!/usr/bin/env python3
"""
Test script to verify the AI-Powered Resume Matching System setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.config import settings
        print("✓ Config loaded successfully")
        print(f"  - Job roles: {settings.job_roles_list}")
        print(f"  - Allowed extensions: {settings.allowed_extensions_list}")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from app.models.database import Base, engine
        print("✓ Database models imported successfully")
    except Exception as e:
        print(f"✗ Database models import failed: {e}")
        return False
    
    try:
        from app.services.file_service import file_service
        print("✓ File service imported successfully")
    except Exception as e:
        print(f"✗ File service import failed: {e}")
        return False
    
    try:
        from app.services.document_parser import document_parser
        print("✓ Document parser imported successfully")
    except Exception as e:
        print(f"✗ Document parser import failed: {e}")
        return False
    
    try:
        from app.services.vector_service import vector_service
        print("✓ Vector service imported successfully")
    except Exception as e:
        print(f"✗ Vector service import failed: {e}")
        return False
    
    try:
        from app.main import app
        print("✓ FastAPI app imported successfully")
    except Exception as e:
        print(f"✗ FastAPI app import failed: {e}")
        return False
    
    return True

def test_directory_structure():
    """Test if all required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "app",
        "app/models",
        "app/schemas", 
        "app/services",
        "app/api",
        "app/tasks"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            return False
    
    return True

def test_required_files():
    """Test if all required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        "requirements.txt",
        "docker-compose.yml", 
        "Dockerfile",
        ".env",
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/models/database.py",
        "app/models/resume.py",
        "app/schemas/resume.py",
        "app/services/file_service.py",
        "app/services/document_parser.py",
        "app/services/vector_service.py",
        "app/api/resume_routes.py",
        "app/api/job_routes.py",
        "app/celery_app.py",
        "app/tasks/resume_processing.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            return False
    
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("AI-Powered Resume Matching System - Setup Test")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test directory structure
    if not test_directory_structure():
        all_tests_passed = False
    
    # Test required files
    if not test_required_files():
        all_tests_passed = False
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! System is ready to run.")
        print("\nNext steps:")
        print("1. Start services: docker-compose up -d")
        print("2. Run the application: uvicorn app.main:app --reload")
        print("3. Access API docs: http://localhost:8000/docs")
    else:
        print("❌ SOME TESTS FAILED! Please fix the issues above.")
    print("=" * 60)

if __name__ == "__main__":
    main()