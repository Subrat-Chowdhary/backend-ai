"""
This file contains the endpoint for downloading resumes as Word documents.
You can copy and paste this code into your resume_routes.py file.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.models.database import get_db
from services.document_template_service import document_template_service

# Add this import at the top of your file
# from fastapi import Response
# from services.document_template_service import document_template_service

# Add this endpoint to your router
@router.post("/download/docx")
async def download_resume_as_docx(
    request: dict,
    template: str = "professional",
    db: Session = Depends(get_db)
):
    """
    Generate and download a resume as a Word document
    
    Args:
        request: Dictionary containing resume_data
        template: Template to use (professional, modern, or compact)
    
    Returns:
        Word document as a downloadable file
    """
    try:
        # Validate template
        if template not in ["professional", "modern", "compact"]:
            template = "professional"
        
        # Extract resume data from request
        resume_data = request.get("resume_data", {})
        
        # Generate document
        doc_bytes = document_template_service.generate_resume_document(
            resumes=[resume_data],
            template_name=template
        )
        
        # Create filename
        name = resume_data.get("name", "Resume").replace(" ", "_")
        filename = f"{name}_{template}_resume.docx"
        
        # Return document as downloadable file
        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))