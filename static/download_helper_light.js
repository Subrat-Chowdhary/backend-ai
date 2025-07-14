/**
 * Frontend Helper for Resume Download Functionality - Light Version
 * Use this JavaScript code in your frontend to integrate with the download endpoints
 */

class ResumeDownloadHelper {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Download selected resumes by their IDs
     * @param {Array} resumeIds - Array of resume IDs from search results
     * @param {string} template - Template type: 'professional', 'modern', 'compact'
     * @param {string} filenamePrefix - Prefix for the downloaded file
     */
    async downloadSelectedResumes(resumeIds, template = 'professional', filenamePrefix = 'Selected_Resumes') {
        try {
            const formData = new FormData();
            formData.append('resume_ids', resumeIds.join(','));
            formData.append('template', template);
            formData.append('filename_prefix', filenamePrefix);

            const response = await fetch(`${this.baseUrl}/download_selected_resumes`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Download failed: ${response.statusText} - ${errorText}`);
            }

            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            const filename = contentDisposition 
                ? contentDisposition.split('filename=')[1].replace(/"/g, '')
                : `${filenamePrefix}_${template}_${new Date().toISOString().slice(0,10)}.docx`;

            // Create blob and download
            const blob = await response.blob();
            this.downloadBlob(blob, filename);

            return { success: true, filename, size: blob.size };
        } catch (error) {
            console.error('Download error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Download search results directly
     * @param {string} query - Search query
     * @param {Object} options - Search and download options
     */
    async downloadSearchResults(query, options = {}) {
        try {
            const {
                jobCategory = null,
                limit = 10,
                similarityThreshold = 0.7,
                template = 'professional',
                filenamePrefix = 'Search_Results'
            } = options;

            const formData = new FormData();
            formData.append('query', query);
            if (jobCategory) formData.append('job_category', jobCategory);
            formData.append('limit', limit.toString());
            formData.append('similarity_threshold', similarityThreshold.toString());
            formData.append('template', template);
            formData.append('filename_prefix', filenamePrefix);

            const response = await fetch(`${this.baseUrl}/download_search_results`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Download failed: ${response.statusText} - ${errorText}`);
            }

            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            const filename = contentDisposition 
                ? contentDisposition.split('filename=')[1].replace(/"/g, '')
                : `${filenamePrefix}_${template}_${new Date().toISOString().slice(0,10)}.docx`;

            // Create blob and download
            const blob = await response.blob();
            this.downloadBlob(blob, filename);

            return { success: true, filename, size: blob.size };
        } catch (error) {
            console.error('Download error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get available templates
     */
    async getAvailableTemplates() {
        try {
            const response = await fetch(`${this.baseUrl}/templates`);
            if (!response.ok) {
                throw new Error(`Failed to get templates: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Template fetch error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Helper method to download blob as file
     * @param {Blob} blob - File blob
     * @param {string} filename - Filename for download
     */
    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    /**
     * Create download buttons for search results
     * @param {Array} searchResults - Array of search results
     * @param {HTMLElement} container - Container element to add buttons
     */
    createDownloadButtons(searchResults, container) {
        // Clear existing buttons
        container.innerHTML = '';

        // Create template selector
        const templateSelect = document.createElement('select');
        templateSelect.id = 'template-select';
        templateSelect.innerHTML = `
            <option value="professional">Professional</option>
            <option value="modern">Modern</option>
            <option value="compact">Compact</option>
        `;

        // Create download selected button
        const downloadSelectedBtn = document.createElement('button');
        downloadSelectedBtn.textContent = 'Download Selected';
        downloadSelectedBtn.onclick = () => {
            const selectedIds = this.getSelectedResumeIds();
            if (selectedIds.length === 0) {
                alert('Please select at least one resume');
                return;
            }
            this.downloadSelectedResumes(selectedIds, templateSelect.value, 'Selected_Candidates');
        };

        // Create download all button
        const downloadAllBtn = document.createElement('button');
        downloadAllBtn.textContent = 'Download All Results';
        downloadAllBtn.onclick = () => {
            const allIds = searchResults.map(result => result.id);
            this.downloadSelectedResumes(allIds, templateSelect.value, 'All_Search_Results');
        };

        // Add elements to container
        container.appendChild(document.createTextNode('Template: '));
        container.appendChild(templateSelect);
        container.appendChild(document.createTextNode(' '));
        container.appendChild(downloadSelectedBtn);
        container.appendChild(document.createTextNode(' '));
        container.appendChild(downloadAllBtn);
    }

    /**
     * Helper to get selected resume IDs from checkboxes
     * Assumes checkboxes have class 'resume-checkbox' and data-resume-id attribute
     */
    getSelectedResumeIds() {
        const checkboxes = document.querySelectorAll('.resume-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.dataset.resumeId);
    }
}

// Example HTML integration:
/*
<!-- Add this to your search results page -->
<div id="download-controls"></div>

<script>
const downloadHelper = new ResumeDownloadHelper();

// After search results are loaded
function onSearchComplete(searchResults) {
    const container = document.getElementById('download-controls');
    downloadHelper.createDownloadButtons(searchResults, container);
}

// Example: Download selected resumes
async function downloadSelected() {
    const selectedIds = ['resume-id-1', 'resume-id-2'];
    const result = await downloadHelper.downloadSelectedResumes(selectedIds, 'professional', 'Top_Candidates');
    if (result.success) {
        console.log(`Downloaded: ${result.filename} (${result.size} bytes)`);
    } else {
        console.error('Download failed:', result.error);
    }
}

// Example: Download search results directly
async function downloadSearchResults() {
    const result = await downloadHelper.downloadSearchResults('Python developer', {
        jobCategory: 'Backend',
        limit: 15,
        template: 'modern',
        filenamePrefix: 'Python_Developers'
    });
    if (result.success) {
        console.log(`Downloaded: ${result.filename} (${result.size} bytes)`);
    } else {
        console.error('Download failed:', result.error);
    }
}
</script>
*/

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResumeDownloadHelper;
}

// Make available globally
if (typeof window !== 'undefined') {
    window.ResumeDownloadHelper = ResumeDownloadHelper;
}