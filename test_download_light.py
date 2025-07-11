#!/usr/bin/env python3
"""
Test script for resume download functionality - Light Version
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_search_and_download():
    """Test the complete search and download workflow"""
    print("🧪 Testing Resume Download Functionality (Light Version)")
    print("=" * 60)
    
    # Step 1: Perform a search to get resume IDs
    print("\n1. Performing search to get resume data...")
    search_data = {
        'query': 'Python developer',
        'limit': 5,
        'similarity_threshold': 0.3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/search_profile", data=search_data)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search successful: Found {search_results.get('total_results', 0)} results")
            
            if search_results.get('results'):
                # Extract resume IDs
                resume_ids = [result['id'] for result in search_results['results'][:3]]  # Take first 3
                print(f"📋 Selected resume IDs: {resume_ids}")
                
                # Step 2: Test template listing
                print("\n2. Getting available templates...")
                template_response = requests.get(f"{BASE_URL}/templates")
                if template_response.status_code == 200:
                    templates = template_response.json()
                    print(f"✅ Available templates: {templates.get('templates', [])}")
                else:
                    print(f"❌ Template fetch failed: {template_response.status_code}")
                
                # Step 3: Test download selected resumes
                print("\n3. Testing download selected resumes...")
                for template in ['professional', 'modern', 'compact']:
                    print(f"\n   Testing {template} template...")
                    download_data = {
                        'resume_ids': ','.join(resume_ids),
                        'template': template,
                        'filename_prefix': f'Test_{template}'
                    }
                    
                    download_response = requests.post(f"{BASE_URL}/download_selected_resumes", data=download_data)
                    if download_response.status_code == 200:
                        # Save the file
                        filename = f"test_download_{template}.docx"
                        with open(filename, 'wb') as f:
                            f.write(download_response.content)
                        
                        file_size = len(download_response.content)
                        print(f"   ✅ {template} template: Downloaded {filename} ({file_size} bytes)")
                        
                        # Verify it's a valid Word document
                        if download_response.headers.get('content-type') == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                            print(f"   ✅ Valid Word document format")
                        else:
                            print(f"   ⚠️  Unexpected content type: {download_response.headers.get('content-type')}")
                    else:
                        print(f"   ❌ {template} template failed: {download_response.status_code}")
                        print(f"   Error: {download_response.text}")
                
                # Step 4: Test download search results directly
                print("\n4. Testing download search results directly...")
                search_download_data = {
                    'query': 'Python developer',
                    'limit': 3,
                    'similarity_threshold': 0.3,
                    'template': 'professional',
                    'filename_prefix': 'Direct_Search_Results'
                }
                
                search_download_response = requests.post(f"{BASE_URL}/download_search_results", data=search_download_data)
                if search_download_response.status_code == 200:
                    filename = "test_search_download.docx"
                    with open(filename, 'wb') as f:
                        f.write(search_download_response.content)
                    
                    file_size = len(search_download_response.content)
                    print(f"✅ Direct search download: {filename} ({file_size} bytes)")
                else:
                    print(f"❌ Direct search download failed: {search_download_response.status_code}")
                    print(f"Error: {search_download_response.text}")
                
            else:
                print("❌ No search results found to test download")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_error_cases():
    """Test error handling"""
    print("\n\n🧪 Testing Error Cases")
    print("=" * 30)
    
    # Test with invalid resume IDs
    print("\n1. Testing with invalid resume IDs...")
    invalid_data = {
        'resume_ids': 'invalid-id-1,invalid-id-2',
        'template': 'professional',
        'filename_prefix': 'Invalid_Test'
    }
    
    response = requests.post(f"{BASE_URL}/download_selected_resumes", data=invalid_data)
    if response.status_code == 404:
        print("✅ Correctly handled invalid resume IDs (404 error)")
    else:
        print(f"⚠️  Unexpected response for invalid IDs: {response.status_code}")
    
    # Test with empty resume IDs
    print("\n2. Testing with empty resume IDs...")
    empty_data = {
        'resume_ids': '',
        'template': 'professional',
        'filename_prefix': 'Empty_Test'
    }
    
    response = requests.post(f"{BASE_URL}/download_selected_resumes", data=empty_data)
    if response.status_code == 400:
        print("✅ Correctly handled empty resume IDs (400 error)")
    else:
        print(f"⚠️  Unexpected response for empty IDs: {response.status_code}")

def cleanup_test_files():
    """Clean up test files"""
    print("\n\n🧹 Cleaning up test files...")
    test_files = [
        'test_download_professional.docx',
        'test_download_modern.docx',
        'test_download_compact.docx',
        'test_search_download.docx'
    ]
    
    for filename in test_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Removed {filename}")

if __name__ == "__main__":
    print("🚀 Starting Resume Download Tests (Light Version)")
    print("Make sure your light server is running on http://localhost:8000")
    print("And that you have some resumes uploaded and indexed")
    
    input("\nPress Enter to continue...")
    
    try:
        # Test main functionality
        test_search_and_download()
        
        # Test error cases
        test_error_cases()
        
        print("\n\n✅ All tests completed!")
        print("\nGenerated files:")
        print("- test_download_professional.docx")
        print("- test_download_modern.docx") 
        print("- test_download_compact.docx")
        print("- test_search_download.docx")
        
        # Ask if user wants to clean up
        cleanup = input("\nDo you want to clean up test files? (y/n): ")
        if cleanup.lower() == 'y':
            cleanup_test_files()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Tests failed with error: {e}")