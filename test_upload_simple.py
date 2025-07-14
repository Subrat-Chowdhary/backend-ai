#!/usr/bin/env python3
"""
Test script for the simplified upload-only functionality (no job categories)
"""
import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("test_files")

def create_test_files():
    """Create test files for upload testing"""
    TEST_FILES_DIR.mkdir(exist_ok=True)
    
    # Create a simple text file
    with open(TEST_FILES_DIR / "test_resume.txt", "w") as f:
        f.write("""
John Doe
Software Engineer
Email: john.doe@email.com
Phone: +1-234-567-8900

EXPERIENCE:
- 5 years of Python development
- FastAPI and Django experience
- AWS cloud services
- Docker and Kubernetes

EDUCATION:
- Bachelor's in Computer Science
- Master's in Software Engineering

SKILLS:
Python, JavaScript, React, Node.js, PostgreSQL, MongoDB
        """)
    
    # Create another test file
    with open(TEST_FILES_DIR / "jane_smith_resume.txt", "w") as f:
        f.write("""
Jane Smith
Frontend Developer
Email: jane.smith@email.com
Phone: +1-987-654-3210

EXPERIENCE:
- 3 years of React development
- Vue.js and Angular experience
- UI/UX design
- Responsive web design

EDUCATION:
- Bachelor's in Web Design
- Frontend Development Bootcamp

SKILLS:
React, Vue.js, Angular, HTML5, CSS3, JavaScript, TypeScript
        """)
    
    print(f"✅ Test files created in {TEST_FILES_DIR}")

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root Endpoint Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_single_file_upload():
    """Test single file upload"""
    try:
        files = {
            'files': ('test_resume.txt', open(TEST_FILES_DIR / 'test_resume.txt', 'rb'), 'text/plain')
        }
        data = {
            'description': 'Test single file upload'
        }
        
        response = requests.post(f"{BASE_URL}/upload_profile", files=files, data=data)
        print(f"\n📤 Single File Upload Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        files['files'][1].close()  # Close file handle
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Single file upload failed: {e}")
        return False

def test_multiple_file_upload():
    """Test multiple file upload"""
    try:
        files = [
            ('files', ('test_resume.txt', open(TEST_FILES_DIR / 'test_resume.txt', 'rb'), 'text/plain')),
            ('files', ('jane_smith_resume.txt', open(TEST_FILES_DIR / 'jane_smith_resume.txt', 'rb'), 'text/plain'))
        ]
        data = {
            'description': 'Test multiple file upload'
        }
        
        response = requests.post(f"{BASE_URL}/upload_profile", files=files, data=data)
        print(f"\n📤 Multiple File Upload Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Close file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Multiple file upload failed: {e}")
        return False

def test_invalid_file_upload():
    """Test upload with invalid file type"""
    try:
        # Create an invalid file
        invalid_file_path = TEST_FILES_DIR / "invalid_file.xyz"
        with open(invalid_file_path, "w") as f:
            f.write("This is an invalid file type")
        
        files = {
            'files': ('invalid_file.xyz', open(invalid_file_path, 'rb'), 'application/octet-stream')
        }
        data = {
            'description': 'Test invalid file upload'
        }
        
        response = requests.post(f"{BASE_URL}/upload_profile", files=files, data=data)
        print(f"\n❌ Invalid File Upload Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        files['files'][1].close()  # Close file handle
        os.unlink(invalid_file_path)  # Clean up
        
        # Should return 200 but with rejected files
        return response.status_code == 200 and len(response.json().get('rejected_files', [])) > 0
    except Exception as e:
        print(f"❌ Invalid file upload test failed: {e}")
        return False

def test_debug_buckets():
    """Test debug buckets endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/debug/buckets")
        print(f"\n🔍 Debug Buckets Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Debug buckets failed: {e}")
        return False

def test_search_endpoint():
    """Test search endpoint (should work even without processed data)"""
    try:
        data = {
            'query': 'Python developer',
            'limit': 5,
            'similarity_threshold': 0.5
        }
        
        response = requests.post(f"{BASE_URL}/search_profile", data=data)
        print(f"\n🔍 Search Test Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Simplified Upload Service Tests (No Job Categories)")
    print("=" * 60)
    
    # Create test files
    create_test_files()
    
    # Run tests
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Health Check", test_health_check),
        ("Single File Upload", test_single_file_upload),
        ("Multiple File Upload", test_multiple_file_upload),
        ("Invalid File Upload", test_invalid_file_upload),
        ("Debug Buckets", test_debug_buckets),
        ("Search Endpoint", test_search_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
        print(f"Result: {'✅ PASSED' if result else '❌ FAILED'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Upload service is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the service configuration.")
    
    # Cleanup
    import shutil
    if TEST_FILES_DIR.exists():
        shutil.rmtree(TEST_FILES_DIR)
        print(f"🧹 Cleaned up test files from {TEST_FILES_DIR}")

if __name__ == "__main__":
    main()