#!/usr/bin/env python3
"""
Test script for AI-Powered Resume Matching System API
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            print(f"  Status: {data.get('status', 'unknown')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✓" if "healthy" in status else "✗"
                print(f"  {status_icon} {service}: {status}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Root endpoint working")
            print(f"  Message: {data.get('message', 'N/A')}")
            print(f"  Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Root endpoint failed: {e}")
        return False

def test_config_endpoint():
    """Test config endpoint"""
    print("\nTesting config endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Config endpoint working")
            print(f"  Job roles: {data.get('job_roles', [])}")
            print(f"  Allowed extensions: {data.get('allowed_extensions', [])}")
            print(f"  Max file size: {data.get('max_file_size', 'N/A')} bytes")
            return True
        else:
            print(f"✗ Config endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Config endpoint failed: {e}")
        return False

def test_resumes_list():
    """Test resumes list endpoint"""
    print("\nTesting resumes list...")
    try:
        response = requests.get(f"{BASE_URL}/resumes/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Resumes list working (found {len(data)} resumes)")
            return True
        else:
            print(f"✗ Resumes list failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Resumes list failed: {e}")
        return False

def test_jobs_list():
    """Test job descriptions list endpoint"""
    print("\nTesting job descriptions list...")
    try:
        response = requests.get(f"{BASE_URL}/jobs/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Job descriptions list working (found {len(data)} jobs)")
            return True
        else:
            print(f"✗ Job descriptions list failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Job descriptions list failed: {e}")
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    print("\nTesting stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/resumes/stats/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Stats endpoint working")
            print(f"  Total resumes: {data.get('total_resumes', 0)}")
            print(f"  Processed resumes: {data.get('processed_resumes', 0)}")
            print(f"  Processing rate: {data.get('processing_rate', 0)}%")
            return True
        else:
            print(f"✗ Stats endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Stats endpoint failed: {e}")
        return False

def wait_for_api(max_wait=60):
    """Wait for API to be available"""
    print(f"Waiting for API to be available (max {max_wait}s)...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print(f"✓ API is available after {i+1}s")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < max_wait - 1:
            print(f"  Waiting... ({i+1}/{max_wait})")
            time.sleep(1)
    
    print(f"✗ API not available after {max_wait}s")
    return False

def main():
    """Main test function"""
    print("=" * 60)
    print("AI-Powered Resume Matching System - API Test")
    print("=" * 60)
    
    # Wait for API to be available
    if not wait_for_api():
        print("\n❌ API is not available. Make sure the services are running:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_root_endpoint,
        test_health_check,
        test_config_endpoint,
        test_resumes_list,
        test_jobs_list,
        test_stats_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! API is working correctly.")
        print("\nYou can now:")
        print("1. Visit http://localhost:8000/docs for interactive API docs")
        print("2. Upload resumes using the /resumes/upload endpoint")
        print("3. Create job descriptions using the /jobs/ endpoint")
        print("4. Search for matching resumes using the /resumes/search endpoint")
    else:
        print("❌ SOME TESTS FAILED! Check the services and logs.")
        print("   docker-compose logs")
    
    print("=" * 60)

if __name__ == "__main__":
    main()