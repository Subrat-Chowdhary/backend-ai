# Word Document Resume Download Implementation Guide

This guide will help you implement and test the feature to download resumes as Word documents.

## Files Created

1. `download_docx_endpoint.py` - Contains the endpoint code to add to your resume_routes.py file
2. `frontend_implementation_guide.md` - Guide for implementing the frontend changes
3. `test_docx_endpoint.py` - Script to test the endpoint

## Backend Implementation Steps

### 1. Add the Endpoint to resume_routes.py

Open your resume_routes.py file and make the following changes:

a. Add the necessary imports at the top:
```python
from fastapi import Response
from services.document_template_service import document_template_service
```

b. Add the endpoint code from `download_docx_endpoint.py` to your file.

### 2. Start the Backend Server

For the light version:
```bash
cd /opt/backend-ai
uvicorn app.main:app --reload
```

## Testing the Endpoint

### 1. Using the Test Script

After starting the backend server, run the test script:
```bash
cd /opt/backend-ai
python test_docx_endpoint.py
```

This will:
- Send a request to the endpoint with sample resume data
- Save the generated Word document to the current directory
- Print a success or error message

### 2. Manual Testing with curl

You can also test the endpoint using curl:
```bash
curl -X POST "http://localhost:8000/resumes/download/docx" \
  -H "Content-Type: application/json" \
  -d '{"resume_data": {"name": "Test User", "email_id": "test@example.com", "skills": ["Python", "FastAPI"]}, "template": "professional"}' \
  --output test_resume.docx
```

## Frontend Implementation

Follow the instructions in `frontend_implementation_guide.md` to update your frontend code.

## Troubleshooting

### Common Issues

1. **404 Not Found Error**
   - Make sure the endpoint is correctly added to resume_routes.py
   - Check that the URL path is correct in your frontend code

2. **500 Internal Server Error**
   - Check the backend logs for details
   - Make sure python-docx is installed
   - Verify that document_template_service is imported correctly

3. **Import Errors**
   - If you get an import error for document_template_service, make sure the path is correct
   - The import should be `from services.document_template_service import document_template_service`

4. **Frontend Issues**
   - Check the browser console for errors
   - Make sure the API URL is correct
   - Verify that the resume data is being sent correctly

## Running in Production

For production deployment:

1. Make sure python-docx is included in your requirements file
2. Update your frontend code to use the correct API URL
3. Test thoroughly before deploying

## Additional Resources

- python-docx documentation: https://python-docx.readthedocs.io/
- FastAPI Response documentation: https://fastapi.tiangolo.com/advanced/response-directly/