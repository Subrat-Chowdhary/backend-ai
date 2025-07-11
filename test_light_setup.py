#!/usr/bin/env python3
"""
Quick test to verify light setup is working
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_light_setup():
    """Test basic light setup functionality"""
    print("🧪 Testing Light Setup")
    print("=" * 30)
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed")
            print(f"   MinIO: {health_data.get('minio_status', 'Unknown')}")
            print(f"   Vector: {health_data.get('vector_status', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test templates endpoint
        print("\n2. Testing templates endpoint...")
        response = requests.get(f"{BASE_URL}/templates")
        if response.status_code == 200:
            templates_data = response.json()
            print("✅ Templates endpoint working")
            print(f"   Available templates: {templates_data.get('templates', [])}")
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        print("\n3. Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            root_data = response.json()
            print("✅ Root endpoint working")
            print(f"   Service: {root_data.get('message', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        print("\n✅ Light setup is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Light Setup Test")
    print("Make sure your light server is running: docker-compose -f docker-compose.light.yml up")
    
    if test_light_setup():
        print("\n🎉 Ready to test download functionality!")
        print("Run: python test_single_download_light.py")
    else:
        print("\n❌ Setup issues detected. Please check your server.")
        sys.exit(1)