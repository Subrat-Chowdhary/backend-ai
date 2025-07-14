# File: /opt/backend-ai/services/document_template_service.py

"""
Document Template Service for Light Version
Handles Word document generation for resume exports
"""
import logging
from typing import List, Dict, Optional
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class DocumentTemplateService:
    def __init__(self):
        self.templates = {
            'professional': self._create_professional_template,
            'modern': self._create_modern_template,
            'compact': self._create_compact_template
        }

    def _get_visible_value(self, key: str, resume: Dict, flags: Dict, override_key: Optional[str] = None):
        show_flag = flags.get(f"show_{key}", True)
        if not show_flag:
            return None
        if override_key and resume.get(override_key):
            return resume[override_key]
        return resume.get(key)

    def generate_resume_document(self, resumes: List[Dict], template_name: str = 'professional') -> bytes:
        try:
            if template_name not in self.templates:
                template_name = 'professional'

            doc = self.templates[template_name](resumes)
            doc_bytes = io.BytesIO()
            doc.save(doc_bytes)
            doc_bytes.seek(0)
            return doc_bytes.getvalue()
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            raise Exception(f"Failed to generate document: {str(e)}")

    def _create_professional_template(self, resumes: List[Dict]) -> Document:
        doc = Document()
        for section in doc.sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        title = doc.add_heading('Selected Resume Profiles', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        info_para = doc.add_paragraph()
        info_para.add_run(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        info_para.add_run(f"\nTotal Profiles: {len(resumes)}")
        info_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_page_break()

        for idx, resume in enumerate(resumes, 1):
            self._add_professional_resume(doc, resume, idx)
            if idx < len(resumes):
                doc.add_page_break()

        return doc

    def _add_professional_resume(self, doc: Document, resume: Dict, index: int):
        doc.add_heading(f"Profile #{index}", level=1)
        doc.add_heading('Personal Information', level=2)
        personal_table = doc.add_table(rows=0, cols=2)
        personal_table.style = 'Table Grid'

        flags = resume.get("visibility_flags", {})
        personal_info = []

        def add_row(label, key, override_key=None):
            value = self._get_visible_value(key, resume, flags, override_key)
            if value:
                personal_info.append((label, value))

        add_row("Name", "name")
        add_row("Email", "email_id", "override_email")
        add_row("Phone", "phone_number", "override_phone")
        add_row("Location", "location")
        add_row("Current Job Title", "current_job_title")
        add_row("LinkedIn", "linkedin_url")
        add_row("GitHub", "github_url")

        score = resume.get("similarity_score")
        try:
            score_str = f"{float(score):.2%}" if score is not None else "N/A"
        except:
            score_str = "N/A"
        personal_info.append(("Similarity Score", score_str))

        for label, value in personal_info:
            row = personal_table.add_row()
            row.cells[0].text = label
            row.cells[1].text = str(value)
            row.cells[0].paragraphs[0].runs[0].bold = True

        if resume.get('objective'):
            doc.add_heading('Professional Summary', level=2)
            doc.add_paragraph(resume.get('objective', ''))

        if resume.get('skills'):
            doc.add_heading('Skills', level=2)
            skills = resume.get('skills', [])
            skills_text = ', '.join(skills) if isinstance(skills, list) else str(skills)
            doc.add_paragraph(skills_text)

        if resume.get('experience_summary'):
            doc.add_heading('Experience Summary', level=2)
            doc.add_paragraph(resume.get('experience_summary', ''))

        if resume.get('companies_worked_with_duration'):
            doc.add_heading('Work History', level=2)
            companies = resume.get('companies_worked_with_duration', [])
            for company in companies:
                doc.add_paragraph(f"• {company}", style='List Bullet')

        if resume.get('qualifications_summary'):
            doc.add_heading('Qualifications', level=2)
            doc.add_paragraph(resume.get('qualifications_summary', ''))

        if resume.get('projects'):
            doc.add_heading('Projects', level=2)
            for project in resume.get('projects', []):
                doc.add_paragraph(f"• {project}", style='List Bullet')

        additional_info = []
        if resume.get('availability_status'):
            additional_info.append(f"Availability: {resume.get('availability_status')}")
        if resume.get('work_authorization_status'):
            additional_info.append(f"Work Authorization: {resume.get('work_authorization_status')}")
        if resume.get('_original_filename'):
            additional_info.append(f"Source File: {resume.get('_original_filename')}")

        if additional_info:
            doc.add_heading('Additional Information', level=2)
            for info in additional_info:
                doc.add_paragraph(f"• {info}", style='List Bullet')

    def _create_modern_template(self, resumes: List[Dict]) -> Document:
        doc = Document()
        title = doc.add_heading('Resume Portfolio', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        summary_table = doc.add_table(rows=1, cols=3)
        summary_table.style = 'Light Shading Accent 1'
        headers = summary_table.rows[0].cells
        headers[0].text = 'Total Profiles'
        headers[1].text = 'Generated Date'
        headers[2].text = 'Template'

        data_row = summary_table.add_row()
        data_row.cells[0].text = str(len(resumes))
        data_row.cells[1].text = datetime.now().strftime('%Y-%m-%d')
        data_row.cells[2].text = 'Modern'

        doc.add_page_break()

        for idx, resume in enumerate(resumes, 1):
            self._add_modern_resume(doc, resume, idx)
            if idx < len(resumes):
                doc.add_page_break()
        return doc

    def _add_modern_resume(self, doc: Document, resume: Dict, index: int):
        header = doc.add_paragraph()
        run = header.add_run(f"CANDIDATE #{index:02d}")
        run.bold = True
        run.font.size = Pt(16)
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER

        name_para = doc.add_paragraph()
        name_run = name_para.add_run(resume.get('name', 'Name Not Available').upper())
        name_run.bold = True
        name_run.font.size = Pt(20)
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        contact_info = []
        for key in ['email_id', 'phone_number', 'location']:
            val = resume.get(key)
            if val and val != 'Unknown':
                contact_info.append(val)

        contact_para = doc.add_paragraph(' | '.join(contact_info))
        contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        try:
            score = float(resume.get("similarity_score", 0))
            score_text = f"{score:.1%}"
        except:
            score_text = "N/A"

        score_para = doc.add_paragraph(f"MATCH SCORE: {score_text}")
        score_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _create_compact_template(self, resumes: List[Dict]) -> Document:
        doc = Document()
        for section in doc.sections:
            section.top_margin = Inches(0.3)
            section.bottom_margin = Inches(0.3)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        title = doc.add_heading('Resume Summary Report', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Total Profiles: {len(resumes)}")
        doc.add_paragraph()

        for idx, resume in enumerate(resumes, 1):
            self._add_compact_resume(doc, resume, idx)
            if idx < len(resumes):
                doc.add_paragraph("─" * 80)
        return doc

    def _add_compact_resume(self, doc: Document, resume: Dict, index: int):
        header = doc.add_paragraph()
        try:
            score = float(resume.get("similarity_score", 0))
            score_text = f"{score:.1%}"
        except:
            score_text = "N/A"

        header.add_run(f"{index}. {resume.get('name', 'N/A')} | {resume.get('current_job_title', 'N/A')} | Score: {score_text}").bold = True

        contact_info = [resume.get('email_id', ''), resume.get('phone_number', ''), resume.get('location', '')]
        filtered = [x for x in contact_info if x and x != "Unknown"]
        doc.add_paragraph(f"Contact: {' | '.join(filtered)}")

        skills = resume.get('skills', [])
        if skills:
            if isinstance(skills, list):
                skills_text = ', '.join(skills[:8])
            else:
                skills_text = str(skills)[:100]
            doc.add_paragraph(f"Skills: {skills_text}")

        if resume.get('experience_summary'):
            exp = resume['experience_summary']
            exp = exp[:150] + "..." if len(exp) > 150 else exp
            doc.add_paragraph(f"Experience: {exp}")

        doc.add_paragraph()

    def get_available_templates(self) -> List[str]:
        return list(self.templates.keys())

# Global instance
document_template_service = DocumentTemplateService()
