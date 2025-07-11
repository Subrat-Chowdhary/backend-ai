# Download Functionality Testing Guide - Light Version

## Overview
This guide will help you test the new Word document download functionality for individual resumes in your light version setup.

## What's New
- **Single Resume Download**: New `/download_single_resume` endpoint
- **Word Document Generation**: Professional, Modern, and Compact templates
- **Frontend Integration**: Ready-to-use JavaScript functions

## Prerequisites

### 1. Start the Light Server
```bash
# Make sure you're in the project directory
cd /opt/backend-ai

# Start the light version
docker-compose -f docker-compose.light.yml up -d

# Check if services are running
docker-compose -f docker-compose.light.yml ps
```

### 2. Verify Setup
```bash
# Run basic setup test
python test_light_setup.py
```

### 3. Upload Some Test Resumes (if needed)
```bash
# Upload a few resumes for testing
curl -X POST "http://localhost:8000/upload_profile" \
  -F "files=@/path/to/resume1.pdf" \
  -F "category=software_engineer"
```

## Testing Steps

### Step 1: Basic Functionality Test
```bash
# Run the comprehensive download test
python test_single_download_light.py
```

This test will:
- Search for resumes
- Test all three templates (professional, modern, compact)
- Download Word documents
- Verify file formats
- Test error handling

### Step 2: Manual API Testing

#### Test Single Resume Download
```bash
# First, get a resume ID from search
curl -X POST "http://localhost:8000/search_profile" \
  -F "query=Python developer" \
  -F "limit=5"

# Use a resume ID from the results
curl -X POST "http://localhost:8000/download_single_resume" \
  -F "resume_id=YOUR_RESUME_ID_HERE" \
  -F "template=professional" \
  -F "filename_prefix=Test_Resume" \
  --output test_resume.docx
```

#### Test Different Templates
```bash
# Professional template
curl -X POST "http://localhost:8000/download_single_resume" \
  -F "resume_id=YOUR_RESUME_ID" \
  -F "template=professional" \
  --output professional_resume.docx

# Modern template
curl -X POST "http://localhost:8000/download_single_resume" \
  -F "resume_id=YOUR_RESUME_ID" \
  -F "template=modern" \
  --output modern_resume.docx

# Compact template
curl -X POST "http://localhost:8000/download_single_resume" \
  -F "resume_id=YOUR_RESUME_ID" \
  -F "template=compact" \
  --output compact_resume.docx
```

### Step 3: Frontend Integration

#### Update Your React Component
Replace your existing `downloadResume` function with the new implementation:

```javascript
// Add this to your API_ENDPOINTS
const API_ENDPOINTS = {
  // ... your existing endpoints
  DOWNLOAD_SINGLE_RESUME: `${BASE_URL}/download_single_resume`,
};

// Replace your downloadResume function
const downloadResume = async (resume) => {
  console.log("Download button clicked for:", resume.name);
  
  setDownloadLoading(true);
  
  try {
    const formData = new FormData();
    formData.append('resume_id', resume.id);
    formData.append('template', 'professional'); // or make this configurable
    formData.append('filename_prefix', `Resume_${resume.name.replace(/\s+/g, '_')}`);
    
    const response = await fetch(API_ENDPOINTS.DOWNLOAD_SINGLE_RESUME, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    // Get filename from response headers
    const contentDisposition = response.headers.get('content-disposition');
    let filename = `${resume.name.replace(/\s+/g, '_')}_Complete_Resume.docx`;
    
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
    
    console.log("Word document download completed successfully!");
    
  } catch (error) {
    console.error("Error downloading resume:", error);
    alert(`Failed to download resume: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    setDownloadLoading(false);
  }
};
```

#### Optional: Add Template Selection
```javascript
// Add state for template selection
const [selectedTemplate, setSelectedTemplate] = useState('professional');

// Template selector component
const TemplateSelector = () => (
  <select 
    value={selectedTemplate}
    onChange={(e) => setSelectedTemplate(e.target.value)}
    className="mb-2 px-3 py-1 border rounded"
  >
    <option value="professional">Professional</option>
    <option value="modern">Modern</option>
    <option value="compact">Compact</option>
  </select>
);

// Update the download function to use selected template
formData.append('template', selectedTemplate);
```

## Expected Results

### File Outputs
After running tests, you should see:
- `test_single_download_professional_[Name].docx`
- `test_single_download_modern_[Name].docx`
- `test_single_download_compact_[Name].docx`

### Document Content
Each Word document should contain:
- **Professional Template**: Detailed format with tables and sections
- **Modern Template**: Two-column layout with visual appeal
- **Compact Template**: Condensed format for multiple resumes

### File Verification
- File size: Typically 15-50KB depending on content
- Format: Valid .docx files that open in Word/LibreOffice
- Content: All resume fields properly formatted

## Troubleshooting

### Common Issues

#### 1. Server Not Running
```bash
# Check if containers are running
docker-compose -f docker-compose.light.yml ps

# Restart if needed
docker-compose -f docker-compose.light.yml restart
```

#### 2. No Resumes Found
```bash
# Upload some test resumes first
python demo_upload.py  # if you have this script
# or manually upload via the API
```

#### 3. Download Fails
- Check server logs: `docker-compose -f docker-compose.light.yml logs resume-api`
- Verify resume ID exists in search results
- Check MinIO connection

#### 4. Invalid Word Documents
- Ensure `python-docx` is installed in requirements-light.txt
- Check document_template_service.py for errors

### Debug Commands
```bash
# Check server health
curl http://localhost:8000/health

# Check available templates
curl http://localhost:8000/templates

# Check server logs
docker-compose -f docker-compose.light.yml logs -f resume-api
```

## API Endpoints Summary

### New Endpoint
- **POST** `/download_single_resume`
  - `resume_id`: Resume ID from search results
  - `template`: professional|modern|compact
  - `filename_prefix`: Optional filename prefix
  - Returns: Word document (.docx)

### Existing Endpoints
- **GET** `/templates` - List available templates
- **POST** `/search_profile` - Search resumes
- **POST** `/download_selected_resumes` - Download multiple resumes
- **GET** `/health` - Health check

## Next Steps

1. **Test the functionality** using the provided scripts
2. **Update your frontend** with the new download function
3. **Customize templates** if needed in `document_template_service.py`
4. **Add template selection UI** for better user experience
5. **Monitor performance** with larger resume sets

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Review server logs
3. Verify all prerequisites are met
4. Test with the provided scripts first before frontend integration