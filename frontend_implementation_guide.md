# Resume Word Document Download Implementation Guide

## Backend Implementation

1. Add the necessary imports to your `resume_routes.py` file:
```python
from fastapi import Response
from services.document_template_service import document_template_service
```

2. Add the following endpoint to your `resume_routes.py` file:
```python
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
```

3. Make sure `python-docx` is installed. It should already be in your `requirements-light.txt` file.

## Frontend Implementation

Replace your current `downloadResume` function in `/home/ahomtechnologies/Projects/ai-resume-matcher/resume-matching-frontend/app/search/page.tsx` with the following:

```typescript
// Download function - Generate comprehensive resume file in Word format
const downloadResume = async (resume: SearchResult) => {
  console.log("Download button clicked for:", resume.name);
  
  setDownloadLoading(true);
  
  try {
    // Call the backend API to generate a Word document
    const response = await fetch('/api/resumes/download/docx', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_data: resume,
        template: 'professional' // You can make this a user choice if needed
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to generate document: ${response.statusText}`);
    }
    
    // Get the blob from the response
    const blob = await response.blob();
    
    // Create a temporary URL for the blob
    const url = URL.createObjectURL(blob);
    
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `${resume.name.replace(/\s+/g, '_')}_Resume.docx`;
    link.style.display = 'none';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up the temporary URL
    URL.revokeObjectURL(url);
    console.log("Download completed successfully!");
    
  } catch (error) {
    console.error("Error downloading resume:", error);
    alert(`Failed to download resume: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    setDownloadLoading(false);
  }
};
```

## Optional: Add Template Selection

If you want to allow users to select different templates, you can add a dropdown menu:

```typescript
// Add this to your component's state
const [selectedTemplate, setSelectedTemplate] = useState('professional');

// Add this dropdown near the download button
<select 
  value={selectedTemplate} 
  onChange={(e) => setSelectedTemplate(e.target.value)}
  className="p-2 border rounded"
>
  <option value="professional">Professional</option>
  <option value="modern">Modern</option>
  <option value="compact">Compact</option>
</select>

// Then update the fetch call in downloadResume
body: JSON.stringify({
  resume_data: resume,
  template: selectedTemplate
}),
```

## Testing the Implementation

1. Start your backend server:
```bash
cd /opt/backend-ai
uvicorn app.main:app --reload
```

2. Start your frontend server:
```bash
cd /home/ahomtechnologies/Projects/ai-resume-matcher/resume-matching-frontend
npm run dev
```

3. Navigate to the search page and try downloading a resume.

## Troubleshooting

- If you get a 404 error, make sure the endpoint is correctly added to your `resume_routes.py` file.
- If you get a 500 error, check the backend logs for details.
- If the download doesn't start, check the browser console for errors.