"""
Document Processing Service for MVP
Handles text extraction from PDF, DOCX, DOC files
"""
import logging
import io
import tempfile
import os
from typing import Optional

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        pass
    
    async def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from document based on file type"""
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return await self._extract_from_pdf(file_content)
            elif file_extension in ['docx', 'doc']:
                return await self._extract_from_docx(file_content)
            else:
                raise Exception(f"Unsupported file type: {file_extension}")
        
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            # Return filename as fallback text
            return f"Document: {filename}"
    
    async def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            # For MVP, we'll use a simple approach
            # In production, you'd use PyPDF2 or pdfplumber
            import PyPDF2
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        
        except ImportError:
            # Fallback if PyPDF2 not available
            logger.warning("PyPDF2 not available, using filename as text")
            return "PDF document content"
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return "PDF document content"
    
    async def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX/DOC file"""
        try:
            # For MVP, we'll use a simple approach
            # In production, you'd use python-docx
            import docx
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            try:
                doc = docx.Document(temp_path)
                text = ""
                
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                
                return text.strip()
            
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except ImportError:
            # Fallback if python-docx not available
            logger.warning("python-docx not available, using filename as text")
            return "DOCX document content"
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return "DOCX document content"

# Global instance
document_service = DocumentService()