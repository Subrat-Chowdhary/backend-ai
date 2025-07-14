#!/usr/bin/env python3
"""
Simple test for extraction functions
"""

import re
from typing import Optional, Tuple

def extract_location(text: str) -> Optional[str]:
    """Extract location/address from text"""
    location_patterns = [
        r'(?:Address|Location|City)[:\s]+([A-Za-z\s,]+(?:,\s*[A-Za-z\s]+)*)',
        r'([A-Za-z\s]+,\s*[A-Za-z\s]+,\s*\d{5,6})',  # City, State, PIN
        r'([A-Za-z\s]+,\s*[A-Za-z\s]+)',  # City, State
        r'(?:Based in|Located in|From)[:\s]+([A-Za-z\s,]+)',
    ]
    
    text_lines = text.split('\n')[:10]  # Check first 10 lines
    
    for line in text_lines:
        line = line.strip()
        for pattern in location_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Basic validation
                if 2 <= len(location) <= 100 and not any(char.isdigit() for char in location[:5]):
                    return location
    
    return None

def extract_current_ctc(text: str) -> Optional[str]:
    """Extract current CTC from text"""
    ctc_patterns = [
        r'(?:Current\s*CTC|CTC|Salary)[:\s]*(?:Rs\.?\s*|INR\s*|₹\s*)?(\d+(?:\.\d+)?\s*(?:LPA|Lakhs?|L|K|Thousands?)?)',
        r'(?:Current\s*Package|Package)[:\s]*(?:Rs\.?\s*|INR\s*|₹\s*)?(\d+(?:\.\d+)?\s*(?:LPA|Lakhs?|L|K|Thousands?)?)',
        r'(?:Earning|Income)[:\s]*(?:Rs\.?\s*|INR\s*|₹\s*)?(\d+(?:\.\d+)?\s*(?:LPA|Lakhs?|L|K|Thousands?)?)',
    ]
    
    text_lower = text.lower()
    
    for pattern in ctc_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            return matches[0].strip()
    
    return None

def extract_notice_period(text: str) -> Optional[str]:
    """Extract notice period from text"""
    notice_patterns = [
        r'(?:Notice\s*Period|Notice)[:\s]*(\d+\s*(?:days?|weeks?|months?))',
        r'(?:Available\s*in|Can\s*join\s*in)[:\s]*(\d+\s*(?:days?|weeks?|months?))',
        r'(?:Serving\s*notice|Notice\s*period)[:\s]*(\d+\s*(?:days?|weeks?|months?))',
    ]
    
    text_lower = text.lower()
    
    for pattern in notice_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], str):
                return matches[0].strip()
            else:
                return matches[0]
    
    # Check for immediate availability
    if re.search(r'(?:immediate|immediately\s*available)', text_lower):
        return "Immediate"
    
    return None

def split_name(full_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Split full name into first name and last name"""
    if not full_name:
        return None, None
    
    name_parts = full_name.strip().split()
    if len(name_parts) == 1:
        return name_parts[0], None
    elif len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])
        return first_name, last_name
    
    return None, None

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
    """
    
    print("🧪 Testing Enhanced Resume Extraction...")
    print("=" * 50)
    
    # Test individual functions
    full_name = "Hritik Kumar Behera"
    first_name, last_name = split_name(full_name)
    location = extract_location(sample_resume_text)
    ctc = extract_current_ctc(sample_resume_text)
    notice = extract_notice_period(sample_resume_text)
    
    print("📋 Extracted Information:")
    print("-" * 30)
    print(f"Full Name: {full_name}")
    print(f"First Name: {first_name}")
    print(f"Last Name: {last_name}")
    print(f"Location: {location}")
    print(f"Current CTC: {ctc}")
    print(f"Notice Period: {notice}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    
    # Verify expected results
    expected_results = {
        'first_name': 'Hritik',
        'last_name': 'Kumar Behera',
        'location': 'Bhubaneswar, Odisha',
        'current_ctc': '5 lpa',
        'notice_period': '30 days'
    }
    
    actual_results = {
        'first_name': first_name,
        'last_name': last_name,
        'location': location,
        'current_ctc': ctc,
        'notice_period': notice
    }
    
    print("\n🔍 Verification:")
    print("-" * 20)
    all_passed = True
    
    for key, expected in expected_results.items():
        actual = actual_results.get(key)
        if actual and expected.lower() in actual.lower():
            print(f"✅ {key}: PASS ({actual})")
        else:
            print(f"❌ {key}: FAIL (Expected: {expected}, Got: {actual})")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check extraction logic.")

if __name__ == "__main__":
    test_extraction()