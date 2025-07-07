# Resume Extraction Enhancement - Testing Guide

## Changes Made

### 1. Enhanced Document Parser
- Added extraction for First Name, Last Name (separately)
- Added Location extraction
- Added Current CTC extraction  
- Added Notice Period extraction
- Added Total Experience extraction (more detailed)

### 2. Database Schema Updates
- Added new fields to Resume model:
  - `candidate_first_name`
  - `candidate_last_name`
  - `candidate_location`
  - `current_ctc`
  - `notice_period`
  - `total_experience`

### 3. New API Endpoint
- Added `/resumes/search/cards` endpoint
- Returns card-friendly format with all extracted info

## Local Testing Steps

### Step 1: Setup Local Environment
```bash
# Clone your repo locally
git clone https://github.com/Subrat-Chowdhary/backend-ai.git
cd backend-ai

# Create a new branch for testing
git checkout -b feature/enhanced-resume-extraction

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Migration
```bash
# Run the migration script to add new fields
python migration_add_candidate_fields.py
```

### Step 3: Test the Changes
```bash
# Start the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test with a sample resume upload
curl -X POST "http://localhost:8000/resumes/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.pdf" \
  -F "job_role=Backend"

# Test the new search endpoint
curl -X POST "http://localhost:8000/resumes/search/cards" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for Python developer",
    "job_role": "Backend",
    "limit": 10,
    "similarity_threshold": 0.3
  }'
```

### Step 4: Expected Response Format
The new `/resumes/search/cards` endpoint will return:
```json
[
  {
    "id": "950bc966-3316-4798-9888-2d1972bf3041",
    "similarity_score": 0.4303884,
    "first_name": "Hritik",
    "last_name": "Kumar Behera",
    "full_name": "Hritik Kumar Behera",
    "location": "Bhubaneswar, Odisha",
    "total_experience": "2 years",
    "current_ctc": "5 LPA",
    "notice_period": "30 days",
    "job_category": "QA",
    "skills": ["Python", "Selenium", "JavaScript"],
    "filename": "Hritik Kumar Behera SoftWare Tester 2- years.pdf",
    "minio_path": "resumes-qa/20250705_112914_Hritik Kumar Behera SoftWare Tester 2- years.pdf",
    "upload_timestamp": "2025-07-05T11:29:15.212652",
    "text_preview": "Responsibilities and Achievements: Understanding business requirements..."
  }
]
```

## Files Modified

1. `app/services/document_parser.py` - Enhanced extraction logic
2. `app/models/resume.py` - Added new database fields
3. `app/schemas/resume.py` - Updated schemas and added ResumeCardInfo
4. `app/api/resume_routes.py` - Added new search endpoint
5. `app/tasks/resume_processing.py` - Updated to handle new fields
6. `migration_add_candidate_fields.py` - Database migration script

## Testing Checklist

- [ ] Database migration runs successfully
- [ ] Resume upload works with new extraction
- [ ] New fields are populated correctly
- [ ] `/resumes/search/cards` endpoint returns expected format
- [ ] First name, last name are extracted separately
- [ ] Location, CTC, notice period are extracted
- [ ] Total experience is extracted properly
- [ ] Existing functionality still works

## Rollback Plan

If issues occur, you can rollback by:
1. Switching back to main branch
2. Running database rollback (if needed)
3. Restarting services

## Production Deployment

Only after successful local testing:
1. Merge feature branch to main
2. Run migration on production database
3. Deploy updated code
4. Monitor logs for any issues