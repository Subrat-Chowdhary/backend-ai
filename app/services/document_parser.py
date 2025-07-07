import os
import re
import logging
from typing import Dict, List, Optional, Tuple
import PyPDF2
import docx2txt
from docx import Document
import spacy
from transformers import pipeline

logger = logging.getLogger(__name__)


class DocumentParser:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. NER functionality will be limited.")
            self.nlp = None
        
        # Load Hugging Face NER pipeline
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
        except Exception as e:
            logger.warning(f"Could not load HF NER model: {e}")
            self.ner_pipeline = None
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            # Try with docx2txt first (simpler)
            text = docx2txt.process(file_path)
            if text.strip():
                return text.strip()
            
            # Fallback to python-docx
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file (legacy format)"""
        try:
            # For DOC files, we'll try to use docx2txt which sometimes works
            text = docx2txt.process(file_path)
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Error extracting text from DOC {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        file_type = file_type.lower()
        
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return self.extract_text_from_docx(file_path)
        elif file_type == "doc":
            return self.extract_text_from_doc(file_path)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return ""
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Multiple phone patterns
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b',  # 1234567890
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # +1-123-456-7890
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def extract_name_with_spacy(self, text: str) -> Optional[str]:
        """Extract person name using spaCy NER"""
        if not self.nlp:
            return None
        
        try:
            doc = self.nlp(text[:1000])  # Process first 1000 chars for efficiency
            persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            
            # Return the first person name found
            if persons:
                # Clean up the name (remove extra whitespace, etc.)
                name = persons[0].strip()
                # Basic validation - name should be 2-50 characters
                if 2 <= len(name) <= 50 and not any(char.isdigit() for char in name):
                    return name
            
            return None
        except Exception as e:
            logger.error(f"Error in spaCy NER: {e}")
            return None
    
    def extract_name_with_hf(self, text: str) -> Optional[str]:
        """Extract person name using Hugging Face NER"""
        if not self.ner_pipeline:
            return None
        
        try:
            # Process first 500 characters for efficiency
            entities = self.ner_pipeline(text[:500])
            
            for entity in entities:
                if entity['entity_group'] == 'PER' and entity['score'] > 0.8:
                    name = entity['word'].strip()
                    # Basic validation
                    if 2 <= len(name) <= 50 and not any(char.isdigit() for char in name):
                        return name
            
            return None
        except Exception as e:
            logger.error(f"Error in HF NER: {e}")
            return None
    
    def extract_name_with_patterns(self, text: str) -> Optional[str]:
        """Extract name using regex patterns"""
        # Look for common resume patterns
        patterns = [
            r'^([A-Z][a-z]+ [A-Z][a-z]+)',  # First line with capitalized words
            r'Name[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',  # "Name: John Doe"
            r'([A-Z][A-Z\s]+)\n',  # ALL CAPS name at beginning
        ]
        
        lines = text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1).strip()
                    # Validate name
                    if 2 <= len(name) <= 50 and ' ' in name:
                        return name
        
        return None
    
    def extract_location(self, text: str) -> Optional[str]:
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
    
    def extract_current_ctc(self, text: str) -> Optional[str]:
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
    
    def extract_notice_period(self, text: str) -> Optional[str]:
        """Extract notice period from text"""
        notice_patterns = [
            r'(?:Notice\s*Period|Notice)[:\s]*(\d+\s*(?:days?|weeks?|months?))',
            r'(?:Available\s*in|Can\s*join\s*in)[:\s]*(\d+\s*(?:days?|weeks?|months?))',
            r'(?:Serving\s*notice|Notice\s*period)[:\s]*(\d+\s*(?:days?|weeks?|months?))',
            r'(?:Immediate|Immediately\s*available)',
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
    
    def extract_total_experience(self, text: str) -> Optional[str]:
        """Extract total years of experience with more detailed patterns"""
        experience_patterns = [
            r'(?:Total\s*Experience|Overall\s*Experience)[:\s]*(\d+(?:\.\d+)?\+?\s*(?:years?|yrs?))',
            r'(\d+(?:\.\d+)?\+?)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:total\s*)?experience',
            r'(?:Experience|Exp)[:\s]*(\d+(?:\.\d+)?\+?\s*(?:years?|yrs?))',
            r'(\d+(?:\.\d+)?\+?)\s*(?:years?|yrs?)\s*(?:in\s*(?:the\s*)?(?:field|industry|IT|software))',
        ]
        
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                exp_text = matches[0].strip()
                # Extract just the number part
                number_match = re.search(r'(\d+(?:\.\d+)?\+?)', exp_text)
                if number_match:
                    return f"{number_match.group(1)} years"
        
        return None
    
    def split_name(self, full_name: str) -> Tuple[Optional[str], Optional[str]]:
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

    def extract_candidate_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract comprehensive candidate information from resume text"""
        # Extract full name first
        full_name = (
            self.extract_name_with_spacy(text) or
            self.extract_name_with_hf(text) or
            self.extract_name_with_patterns(text)
        )
        
        # Split name into first and last
        first_name, last_name = self.split_name(full_name)
        
        info = {
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "location": self.extract_location(text),
            "current_ctc": self.extract_current_ctc(text),
            "notice_period": self.extract_notice_period(text),
            "total_experience": self.extract_total_experience(text)
        }
        
        return info
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common technical skills (this could be expanded or made configurable)
        skill_keywords = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "php", "ruby", "swift", "kotlin", "scala", "r", "matlab",
            
            # Web Technologies
            "html", "css", "react", "angular", "vue", "node.js", "express",
            "django", "flask", "fastapi", "spring", "laravel",
            
            # Databases
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "oracle", "sql server", "sqlite", "cassandra",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
            "terraform", "ansible", "git", "github", "gitlab",
            
            # Data Science & ML
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "jupyter", "tableau",
            
            # Other Technologies
            "linux", "windows", "macos", "apache", "nginx", "microservices",
            "rest api", "graphql", "websockets", "oauth", "jwt"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def estimate_experience_years(self, text: str) -> Optional[float]:
        """Estimate years of experience from resume text"""
        # Look for experience patterns
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
        ]
        
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    years = float(matches[0])
                    if 0 <= years <= 50:  # Reasonable range
                        return years
                except ValueError:
                    continue
        
        return None
    
    def categorize_job_role(self, text: str, skills: List[str]) -> Tuple[Optional[str], Optional[float]]:
        """Categorize job role based on text and skills"""
        text_lower = text.lower()
        
        # Define role keywords and their weights
        role_keywords = {
            "Backend": ["backend", "server", "api", "database", "python", "java", "node.js", "django", "flask", "spring"],
            "Frontend": ["frontend", "ui", "ux", "react", "angular", "vue", "javascript", "html", "css", "web design"],
            "Fullstack": ["fullstack", "full stack", "full-stack", "end-to-end", "frontend and backend"],
            "DevOps": ["devops", "deployment", "ci/cd", "docker", "kubernetes", "aws", "azure", "jenkins", "terraform"],
            "QA": ["qa", "quality assurance", "testing", "test automation", "selenium", "cypress", "junit"],
            "Database": ["dba", "database administrator", "sql", "mysql", "postgresql", "oracle", "data modeling"],
            "Mobile": ["mobile", "android", "ios", "react native", "flutter", "swift", "kotlin"],
            "DataScience": ["data scientist", "machine learning", "deep learning", "ai", "tensorflow", "pytorch", "pandas"]
        }
        
        role_scores = {}
        
        for role, keywords in role_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
                if keyword.title() in skills:
                    score += 2  # Skills have higher weight
            
            if score > 0:
                role_scores[role] = score
        
        if role_scores:
            best_role = max(role_scores, key=role_scores.get)
            max_score = role_scores[best_role]
            total_keywords = len(role_keywords[best_role])
            confidence = min(max_score / total_keywords, 1.0)
            
            return best_role, confidence
        
        return None, None
    
    def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """Parse resume and extract all information"""
        # Extract raw text
        raw_text = self.extract_text(file_path, file_type)
        
        if not raw_text:
            return {
                "raw_text": "",
                "processed_text": "",
                "candidate_info": {"name": None, "email": None, "phone": None},
                "skills": [],
                "experience_years": None,
                "job_role": None,
                "job_role_confidence": None,
                "error": "Could not extract text from file"
            }
        
        # Clean and process text
        processed_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Extract candidate information
        candidate_info = self.extract_candidate_info(raw_text)
        
        # Extract skills
        skills = self.extract_skills(raw_text)
        
        # Estimate experience
        experience_years = self.estimate_experience_years(raw_text)
        
        # Categorize job role
        job_role, job_role_confidence = self.categorize_job_role(raw_text, skills)
        
        return {
            "raw_text": raw_text,
            "processed_text": processed_text,
            "candidate_info": candidate_info,
            "skills": skills,
            "experience_years": experience_years,
            "job_role": job_role,
            "job_role_confidence": job_role_confidence,
            "error": None
        }


# Global document parser instance
document_parser = DocumentParser()