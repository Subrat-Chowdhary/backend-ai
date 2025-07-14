"""
Test script for the resume download endpoint
"""
import requests
import json
import os

# Sample resume data (similar to what would be sent from the frontend)
sample_resume = {
    "name": "John Doe",
    "email_id": "john.doe@example.com",
    "phone_number": "123-456-7890",
    "location": "New York, NY",
    "current_job_title": "Senior Software Engineer",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "github_url": "https://github.com/johndoe",
    "objective": "Experienced software engineer with a passion for building scalable applications.",
    "skills": ["Python", "JavaScript", "React", "FastAPI", "Docker"],
    "experience_summary": "Over 8 years of experience in software development with a focus on web applications.",
    "qualifications_summary": "Bachelor's in Computer Science, AWS Certified Developer",
    "companies_worked_with_duration": [
        "ABC Tech (2018-2023)",
        "XYZ Solutions (2015-2018)"
    ],
    "certifications": ["AWS Certified Developer", "Microsoft Certified: Azure Developer Associate"],
    "awards_achievements": ["Employee of the Year 2022", "Innovation Award 2020"],
    "projects": ["E-commerce Platform", "CRM System", "Mobile Banking App"],
    "languages": ["English", "Spanish"],
    "availability_status": "Available in 2 weeks",
    "work_authorization_status": "US Citizen",
    "has_photo": True,
    "_original_filename": "john_doe_resume.pdf",
    "personal_details": "Some personal details",
    "personal_info": "Some personal info",
    "_is_master_record": True,
    "_duplicate_group_id": "group123",
    "_duplicate_count": 0,
    "_associated_original_filenames": ["john_doe_resume.pdf"],
    "_associated_ids": ["123"],
    "similarity_score": 0.95
}

def test_download_endpoint():
    """Test the resume download endpoint"""
    # URL of your API
    url = "http://localhost:8000/resumes/download/docx"
    
    # Data to send
    data = {
        "resume_data": sample_resume,
        "template": "professional"  # Try different templates: professional, modern, compact
    }
    
    # Make the request
    response = requests.post(url, json=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the file
        filename = f"{sample_resume['name'].replace(' ', '_')}_test_resume.docx"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Successfully downloaded resume to {filename}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_download_endpoint()