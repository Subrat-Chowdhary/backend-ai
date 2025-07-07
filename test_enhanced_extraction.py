#!/usr/bin/env python3
"""
Test script for enhanced resume extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.document_parser import document_parser

def test_extraction():
    """Test the enhanced extraction with sample resume text"""
    
    sample_resume_text = """
    Hritik Kumar Behera
    Software Tester
    Email: hritik.behera@email.com
    Phone: +91-9876543210
    Location: Bhubaneswar, Odisha
    
    Professional Summary:
    Experienced Software Tester with 2+ years of experience in manual and automation testing.
    
    Current CTC: 5 LPA
    Notice Period: 30 days
    Total Experience: 2 years
    
    Skills:
    - Python
    - Selenium WebDriver
    - JavaScript
    - Test Automation
    - Manual Testing
    
    Experience:
    Software Tester | ABC Company | 2022 - Present
    - Understanding business requirements and specifications
    - Creating test cases with element locators and Taiko framework methods
    - Enhancing test cases using JavaScript
    """
    
    print("🧪 Testing Enhanced Resume Extraction...")
    print("=" * 50)
    
    # Test the extraction
    result = document_parser.parse_resume("", "")  # We'll pass text directly
    
    # Override with our sample text for testing
    candidate_info = document_parser.extract_candidate_info(sample_resume_text)
    skills = document_parser.extract_skills(sample_resume_text)
    experience = document_parser.estimate_experience_years(sample_resume_text)
    job_role, confidence = document_parser.categorize_job_role(sample_resume_text, skills)
    
    print("📋 Extracted Information:")
    print("-" * 30)
    print(f"Full Name: {candidate_info.get('name')}")
    print(f"First Name: {candidate_info.get('first_name')}")
    print(f"Last Name: {candidate_info.get('last_name')}")
    print(f"Email: {candidate_info.get('email')}")
    print(f"Phone: {candidate_info.get('phone')}")
    print(f"Location: {candidate_info.get('location')}")
    print(f"Current CTC: {candidate_info.get('current_ctc')}")
    print(f"Notice Period: {candidate_info.get('notice_period')}")
    print(f"Total Experience: {candidate_info.get('total_experience')}")
    print(f"Skills: {skills}")
    print(f"Experience Years: {experience}")
    print(f"Job Role: {job_role} (Confidence: {confidence})")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    
    # Verify expected results
    expected_results = {
        'first_name': 'Hritik',
        'last_name': 'Kumar Behera',
        'email': 'hritik.behera@email.com',
        'location': 'Bhubaneswar, Odisha',
        'current_ctc': '5 LPA',
        'notice_period': '30 days'
    }
    
    print("\n🔍 Verification:")
    print("-" * 20)
    all_passed = True
    
    for key, expected in expected_results.items():
        actual = candidate_info.get(key)
        if actual and expected.lower() in actual.lower():
            print(f"✅ {key}: PASS")
        else:
            print(f"❌ {key}: FAIL (Expected: {expected}, Got: {actual})")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check extraction logic.")

if __name__ == "__main__":
    test_extraction()