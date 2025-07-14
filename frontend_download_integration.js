// Updated Frontend Integration for Single Resume Download
// Replace your existing downloadResume function with this one

const downloadResume = async (resume) => {
  console.log("Download button clicked for:", resume.name);
  
  setDownloadLoading(true);
  
  try {
    // Create form data for the API call
    const formData = new FormData();
    formData.append('resume_id', resume.id);
    formData.append('template', 'professional'); // You can make this configurable
    formData.append('filename_prefix', `Resume_${resume.name.replace(/\s+/g, '_')}`);
    
    // Call the new single resume download endpoint
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}/download_single_resume`, {
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
    
    // Create blob from response
    const blob = await response.blob();
    
    // Verify it's a Word document
    if (blob.type !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      console.warn('Unexpected file type:', blob.type);
    }
    
    // Create temporary URL for the blob
    const url = URL.createObjectURL(blob);
    
    // Create temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up the temporary URL
    URL.revokeObjectURL(url);
    
    console.log("Word document download completed successfully!");
    
  } catch (error) {
    console.error("Error downloading resume:", error);
    alert(`Failed to download resume: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    setDownloadLoading(false);
  }
};

// Optional: Enhanced version with template selection
const downloadResumeWithTemplate = async (resume, template = 'professional') => {
  console.log(`Download button clicked for: ${resume.name} with template: ${template}`);
  
  setDownloadLoading(true);
  
  try {
    const formData = new FormData();
    formData.append('resume_id', resume.id);
    formData.append('template', template);
    formData.append('filename_prefix', `Resume_${resume.name.replace(/\s+/g, '_')}`);
    
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}/download_single_resume`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const contentDisposition = response.headers.get('content-disposition');
    let filename = `${resume.name.replace(/\s+/g, '_')}_${template}_Resume.docx`;
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename=(.+)/);
      if (filenameMatch) {
        filename = filenameMatch[1].replace(/"/g, '');
      }
    }
    
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
    
    console.log(`${template} template download completed successfully!`);
    
  } catch (error) {
    console.error("Error downloading resume:", error);
    alert(`Failed to download resume: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    setDownloadLoading(false);
  }
};

// Template selector component (optional)
const TemplateSelector = ({ onTemplateSelect, selectedTemplate = 'professional' }) => {
  const templates = [
    { value: 'professional', label: 'Professional', description: 'Detailed professional format' },
    { value: 'modern', label: 'Modern', description: 'Modern two-column layout' },
    { value: 'compact', label: 'Compact', description: 'Compact format' }
  ];
  
  return (
    <div className="template-selector">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Select Template:
      </label>
      <select 
        value={selectedTemplate}
        onChange={(e) => onTemplateSelect(e.target.value)}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
      >
        {templates.map(template => (
          <option key={template.value} value={template.value}>
            {template.label} - {template.description}
          </option>
        ))}
      </select>
    </div>
  );
};

// Usage example in your component:
/*
const [selectedTemplate, setSelectedTemplate] = useState('professional');

// In your JSX:
<TemplateSelector 
  selectedTemplate={selectedTemplate}
  onTemplateSelect={setSelectedTemplate}
/>

<button 
  onClick={() => downloadResumeWithTemplate(resume, selectedTemplate)}
  disabled={downloadLoading}
  className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md disabled:opacity-50"
>
  {downloadLoading ? 'Downloading...' : 'Download Complete Resume'}
</button>
*/