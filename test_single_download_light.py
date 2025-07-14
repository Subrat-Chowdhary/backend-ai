#!/usr/bin/env python3
"""
Test script for single resume download functionality - Light Version
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_single_resume_download():
    """Test the single resume download functionality"""
    print("🧪 Testing Single Resume Download Functionality (Light Version)")
    print("=" * 70)
    
    # Step 1: Perform a search to get resume IDs
    print("\n1. Performing search to get resume data...")
    search_data = {
        'query': 'Python developer software engineer',
        'limit': 5,
        'similarity_threshold': 0.3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/search_profile", data=search_data)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search successful: Found {search_results.get('total_results', 0)} results")
            
            if search_results.get('results'):
                # Get first resume for testing
                first_resume = search_results['results'][0]
                resume_id = first_resume['id']
                resume_name = first_resume.get('name', 'Unknown')
                
                print(f"📋 Selected resume: {resume_name} (ID: {resume_id})")
                
                # Step 2: Test template listing
                print("\n2. Getting available templates...")
                template_response = requests.get(f"{BASE_URL}/templates")
                if template_response.status_code == 200:
                    templates = template_response.json()
                    print(f"✅ Available templates: {templates.get('templates', [])}")
                    available_templates = templates.get('templates', ['professional'])
                else:
                    print(f"❌ Template fetch failed: {template_response.status_code}")
                    available_templates = ['professional']
                
                # Step 3: Test single resume download for each template
                print(f"\n3. Testing single resume download for: {resume_name}")
                
                for template in available_templates:
                    print(f"\n   Testing {template} template...")
                    download_data = {
                        'resume_id': resume_id,
                        'template': template,
                        'filename_prefix': f'SingleTest_{template}'
                    }
                    
                    download_response = requests.post(f"{BASE_URL}/download_single_resume", data=download_data)
                    if download_response.status_code == 200:
                        # Save the file
                        filename = f"test_single_download_{template}_{resume_name.replace(' ', '_')}.docx"
                        with open(filename, 'wb') as f:
                            f.write(download_response.content)
                        
                        file_size = len(download_response.content)
                        print(f"   ✅ {template} template: Downloaded {filename} ({file_size} bytes)")
                        
                        # Verify it's a valid Word document
                        content_type = download_response.headers.get('content-type')
                        if content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                            print(f"   ✅ Valid Word document format")
                        else:
                            print(f"   ⚠️  Unexpected content type: {content_type}")
                        
                        # Check filename in headers
                        content_disposition = download_response.headers.get('content-disposition', '')
                        if 'attachment' in content_disposition:
                            print(f"   ✅ Proper download headers set")
                        else:
                            print(f"   ⚠️  Missing download headers")
                            
                    else:
                        print(f"   ❌ {template} template failed: {download_response.status_code}")
                        print(f"   Error: {download_response.text}")
                
                # Step 4: Test with multiple resumes for comparison
                if len(search_results['results']) > 1:
                    print(f"\n4. Testing downloads for multiple resumes...")
                    for i, resume in enumerate(search_results['results'][:3], 1):
                        resume_id = resume['id']
                        resume_name = resume.get('name', f'Resume_{i}')
                        
                        print(f"\n   Downloading resume {i}: {resume_name}")
                        download_data = {
                            'resume_id': resume_id,
                            'template': 'professional',
                            'filename_prefix': f'MultiTest_{i}'
                        }
                        
                        download_response = requests.post(f"{BASE_URL}/download_single_resume", data=download_data)
                        if download_response.status_code == 200:
                            filename = f"test_multi_download_{i}_{resume_name.replace(' ', '_')}.docx"
                            with open(filename, 'wb') as f:
                                f.write(download_response.content)
                            
                            file_size = len(download_response.content)
                            print(f"   ✅ Downloaded: {filename} ({file_size} bytes)")
                        else:
                            print(f"   ❌ Failed: {download_response.status_code}")
                
            else:
                print("❌ No search results found to test download")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_error_cases():
    """Test error handling for single resume download"""
    print("\n\n🧪 Testing Error Cases for Single Resume Download")
    print("=" * 50)
    
    # Test with invalid resume ID
    print("\n1. Testing with invalid resume ID...")
    invalid_data = {
        'resume_id': 'invalid-resume-id-12345',
        'template': 'professional',
        'filename_prefix': 'Invalid_Test'
    }
    
    response = requests.post(f"{BASE_URL}/download_single_resume", data=invalid_data)
    if response.status_code == 404:
        print("✅ Correctly handled invalid resume ID (404 error)")
    else:
        print(f"⚠️  Unexpected response for invalid ID: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test with empty resume ID
    print("\n2. Testing with empty resume ID...")
    empty_data = {
        'resume_id': '',
        'template': 'professional',
        'filename_prefix': 'Empty_Test'
    }
    
    response = requests.post(f"{BASE_URL}/download_single_resume", data=empty_data)
    if response.status_code == 400:
        print("✅ Correctly handled empty resume ID (400 error)")
    else:
        print(f"⚠️  Unexpected response for empty ID: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test with invalid template
    print("\n3. Testing with invalid template...")
    # First get a valid resume ID
    search_data = {'query': 'test', 'limit': 1, 'similarity_threshold': 0.1}
    search_response = requests.post(f"{BASE_URL}/search_profile", data=search_data)
    
    if search_response.status_code == 200:
        search_results = search_response.json()
        if search_results.get('results'):
            resume_id = search_results['results'][0]['id']
            
            invalid_template_data = {
                'resume_id': resume_id,
                'template': 'invalid_template_name',
                'filename_prefix': 'Invalid_Template_Test'
            }
            
            response = requests.post(f"{BASE_URL}/download_single_resume", data=invalid_template_data)
            if response.status_code == 200:
                print("✅ Invalid template handled gracefully (fallback to default)")
            else:
                print(f"⚠️  Unexpected response for invalid template: {response.status_code}")

def cleanup_test_files():
    """Clean up test files"""
    print("\n\n🧹 Cleaning up test files...")
    
    # Find all test files
    test_files = []
    for filename in os.listdir('.'):
        if filename.startswith('test_single_download_') or filename.startswith('test_multi_download_'):
            if filename.endswith('.docx'):
                test_files.append(filename)
    
    for filename in test_files:
        try:
            os.remove(filename)
            print(f"Removed {filename}")
        except Exception as e:
            print(f"Failed to remove {filename}: {e}")

def show_frontend_integration_example():
    """Show example of how to integrate with frontend"""
    print("\n\n📋 Frontend Integration Example")
    print("=" * 40)
    
    print("""
// JavaScript function to download a single resume
const downloadSingleResume = async (resumeId, resumeName, template = 'professional') => {
    try {
        setDownloadLoading(true);
        
        const formData = new FormData();
        formData.append('resume_id', resumeId);
        formData.append('template', template);
        formData.append('filename_prefix', `Resume_${resumeName.replace(/\\s+/g, '_')}`);
        
        const response = await fetch(`${API_BASE_URL}/download_single_resume`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        // Get filename from response headers
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `${resumeName}_Resume.docx`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename=(.+)/);
            if (filenameMatch) {
                filename = filenameMatch[1].replace(/"/g, '');
            }
        }
        
        // Create blob and download
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        console.log('Download completed successfully!');
        
    } catch (error) {
        console.error('Error downloading resume:', error);
        alert(`Failed to download resume: ${error.message}`);
    } finally {
        setDownloadLoading(false);
    }
};

// Usage in your React component:
// <button onClick={() => downloadSingleResume(resume.id, resume.name, 'professional')}>
//   Download Complete Resume
// </button>
    """)

if __name__ == "__main__":
    print("🚀 Starting Single Resume Download Tests (Light Version)")
    print("Make sure your light server is running on http://localhost:8000")
    print("And that you have some resumes uploaded and indexed")
    
    input("\nPress Enter to continue...")
    
    try:
        # Test main functionality
        test_single_resume_download()
        
        # Test error cases
        test_error_cases()
        
        # Show integration example
        show_frontend_integration_example()
        
        print("\n\n✅ All tests completed!")
        
        # List generated files
        test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.docx')]
        if test_files:
            print("\nGenerated files:")
            for filename in test_files:
                file_size = os.path.getsize(filename)
                print(f"- {filename} ({file_size} bytes)")
        
        # Ask if user wants to clean up
        cleanup = input("\nDo you want to clean up test files? (y/n): ")
        if cleanup.lower() == 'y':
            cleanup_test_files()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Tests failed with error: {e}")