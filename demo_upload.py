#!/usr/bin/env python3
"""
Demo script to create sample resumes and test the upload functionality
"""

import requests
import json
import time
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

BASE_URL = "http://localhost:8000"

def create_sample_resume_pdf(name, skills, experience, role):
    """Create a sample PDF resume"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Resume - {name}")
    
    # Contact Info
    p.setFont("Helvetica", 12)
    y = height - 100
    p.drawString(50, y, f"Name: {name}")
    p.drawString(50, y - 20, f"Email: {name.lower().replace(' ', '.')}@email.com")
    p.drawString(50, y - 40, f"Phone: +1-555-{hash(name) % 9000 + 1000}")
    
    # Experience
    y -= 80
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Experience")
    p.setFont("Helvetica", 12)
    p.drawString(50, y - 25, f"{experience} years of experience in {role} development")
    
    # Skills
    y -= 60
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Skills")
    p.setFont("Helvetica", 12)
    skills_text = ", ".join(skills)
    
    # Wrap skills text if too long
    max_width = 500
    if len(skills_text) > 60:
        mid = len(skills_text) // 2
        comma_pos = skills_text.find(', ', mid)
        if comma_pos != -1:
            p.drawString(50, y - 25, skills_text[:comma_pos])
            p.drawString(50, y - 45, skills_text[comma_pos + 2:])
        else:
            p.drawString(50, y - 25, skills_text)
    else:
        p.drawString(50, y - 25, skills_text)
    
    # Projects/Description
    y -= 80
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Summary")
    p.setFont("Helvetica", 12)
    summary = f"Experienced {role} developer with {experience} years of hands-on experience. "
    summary += f"Proficient in {skills[0]} and {skills[1] if len(skills) > 1 else 'various technologies'}. "
    summary += "Strong problem-solving skills and ability to work in agile environments."
    
    # Wrap summary text
    words = summary.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 70:
            lines.append(' '.join(current_line[:-1]))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    for i, line in enumerate(lines[:4]):  # Max 4 lines
        p.drawString(50, y - 25 - (i * 20), line)
    
    p.save()
    buffer.seek(0)
    return buffer

def create_sample_resumes():
    """Create sample resume data"""
    resumes = [
        {
            "name": "John Smith",
            "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
            "experience": 5,
            "role": "Backend"
        },
        {
            "name": "Sarah Johnson",
            "skills": ["React", "JavaScript", "TypeScript", "Node.js", "CSS"],
            "experience": 3,
            "role": "Frontend"
        },
        {
            "name": "Mike Chen",
            "skills": ["Python", "React", "PostgreSQL", "Docker", "Kubernetes"],
            "experience": 7,
            "role": "Fullstack"
        },
        {
            "name": "Emily Davis",
            "skills": ["Jenkins", "Docker", "Kubernetes", "AWS", "Terraform"],
            "experience": 4,
            "role": "DevOps"
        },
        {
            "name": "Alex Rodriguez",
            "skills": ["Selenium", "Python", "Jest", "Cypress", "TestNG"],
            "experience": 6,
            "role": "QA"
        }
    ]
    return resumes

def upload_resume(resume_data):
    """Upload a resume to the API"""
    try:
        # Create PDF
        pdf_buffer = create_sample_resume_pdf(
            resume_data["name"],
            resume_data["skills"],
            resume_data["experience"],
            resume_data["role"]
        )
        
        # Prepare file for upload
        filename = f"{resume_data['name'].replace(' ', '_')}_resume.pdf"
        files = {
            'file': (filename, pdf_buffer.getvalue(), 'application/pdf')
        }
        data = {
            'job_role': resume_data['role']
        }
        
        print(f"Uploading resume for {resume_data['name']}...")
        response = requests.post(
            f"{BASE_URL}/resumes/upload",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully uploaded resume for {resume_data['name']}")
            print(f"  Resume ID: {result.get('id')}")
            print(f"  Status: {result.get('processing_status')}")
            return result
        else:
            print(f"✗ Failed to upload resume for {resume_data['name']}: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error uploading resume for {resume_data['name']}: {e}")
        return None

def create_job_description():
    """Create a sample job description"""
    job_data = {
        "title": "Senior Python Developer",
        "description": """We are looking for an experienced Python developer to join our backend team. 
        The ideal candidate will have strong experience with Python frameworks like Django or FastAPI, 
        database design, and cloud technologies. You will be responsible for developing scalable 
        web applications and APIs.""",
        "requirements": """- 3+ years of Python development experience
        - Experience with Django or FastAPI
        - Strong knowledge of PostgreSQL or similar databases
        - Experience with Docker and containerization
        - Knowledge of AWS or other cloud platforms
        - Experience with Git and agile development practices""",
        "job_role": "Backend",
        "experience_level": "senior",
        "required_skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "preferred_skills": ["FastAPI", "Redis", "Kubernetes", "CI/CD"]
    }
    
    try:
        print("Creating sample job description...")
        response = requests.post(
            f"{BASE_URL}/jobs/",
            json=job_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Successfully created job description")
            print(f"  Job ID: {result.get('id')}")
            print(f"  Title: {result.get('title')}")
            return result
        else:
            print(f"✗ Failed to create job description: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating job description: {e}")
        return None

def search_resumes():
    """Search for matching resumes"""
    search_data = {
        "job_description": "Looking for a Python developer with Django experience and database knowledge",
        "job_role": "Backend",
        "limit": 5,
        "similarity_threshold": 0.3
    }
    
    try:
        print("Searching for matching resumes...")
        response = requests.post(
            f"{BASE_URL}/resumes/search",
            json=search_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Search completed - found {len(result.get('results', []))} matches")
            
            for i, match in enumerate(result.get('results', [])[:3):
                resume = match.get('resume', {})
                print(f"  {i+1}. {resume.get('candidate_name', 'Unknown')} - Score: {match.get('similarity_score', 0):.3f}")
                print(f"     Skills: {resume.get('skills', [])}")
            
            return result
        else:
            print(f"✗ Search failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error during search: {e}")
        return None

def wait_for_processing(max_wait=60):
    """Wait for resumes to be processed"""
    print(f"Waiting for resume processing to complete (max {max_wait}s)...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/resumes/stats/overview", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                total = stats.get('total_resumes', 0)
                processed = stats.get('processed_resumes', 0)
                
                if total > 0 and processed >= total:
                    print(f"✓ All {processed} resumes processed!")
                    return True
                elif total > 0:
                    print(f"  Processing... {processed}/{total} resumes completed")
                
        except requests.exceptions.RequestException:
            pass
        
        if i < max_wait - 1:
            time.sleep(2)
    
    print(f"⚠ Processing may still be ongoing after {max_wait}s")
    return False

def main():
    """Main demo function"""
    print("=" * 60)
    print("AI-Powered Resume Matching System - Demo")
    print("=" * 60)
    
    # Check if reportlab is available
    try:
        import reportlab
    except ImportError:
        print("❌ This demo requires reportlab to create sample PDFs")
        print("Install it with: pip install reportlab")
        return
    
    # Check API availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not available. Make sure services are running:")
            print("   docker-compose up -d")
            return
    except requests.exceptions.RequestException:
        print("❌ API is not available. Make sure services are running:")
        print("   docker-compose up -d")
        return
    
    print("🚀 Starting demo...")
    
    # Create and upload sample resumes
    print("\n1. Creating and uploading sample resumes...")
    resumes = create_sample_resumes()
    uploaded_count = 0
    
    for resume_data in resumes:
        result = upload_resume(resume_data)
        if result:
            uploaded_count += 1
        time.sleep(1)  # Small delay between uploads
    
    print(f"\n📊 Uploaded {uploaded_count}/{len(resumes)} resumes successfully")
    
    if uploaded_count == 0:
        print("❌ No resumes uploaded successfully. Check the API logs.")
        return
    
    # Create job description
    print("\n2. Creating sample job description...")
    job_result = create_job_description()
    
    # Wait for processing
    print("\n3. Waiting for resume processing...")
    wait_for_processing(90)
    
    # Search for matches
    print("\n4. Searching for matching candidates...")
    search_result = search_resumes()
    
    # Show final stats
    print("\n5. Final system stats...")
    try:
        response = requests.get(f"{BASE_URL}/resumes/stats/overview", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"  Total resumes: {stats.get('total_resumes', 0)}")
            print(f"  Processed resumes: {stats.get('processed_resumes', 0)}")
            print(f"  Processing rate: {stats.get('processing_rate', 0)}%")
            
            job_roles = stats.get('job_role_distribution', {})
            if job_roles:
                print("  Job role distribution:")
                for role, count in job_roles.items():
                    print(f"    {role}: {count}")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/docs for interactive API documentation")
    print("2. Try uploading your own resumes")
    print("3. Create custom job descriptions and search queries")
    print("4. Explore the MinIO console at http://localhost:9001")
    print("=" * 60)

if __name__ == "__main__":
    main()