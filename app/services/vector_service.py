from typing import List, Dict, Any, Optional

class VectorService:
    def __init__(self):
        pass
    
    def search_similar_resumes(
        self, 
        query_text: str, 
        job_role: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar resumes using vector similarity"""
        # Mock implementation - returns sample data with exact field names from your payload
        return [
            {
                "collection": "employee_profiles",
                "similarity_score": 0.95,
                "id": "ResumeMadhavKumar",
                "name": "Madhav Kumar",
                "email_id": "madhavkumar279_xiu@indeedemail.com",
                "phone_number": "8010634173",
                "linkedin_url": None,
                "github_url": None,
                "location": "Gurugram, Haryana, India",
                "current_job_title": "Sr. QA Engineer",
                "objective": "Results-driven Sr. QA Engineer with 8 years of experience in Manual Testing, Automation Testing (Java & Selenium), SDLC, STLC, and API Testing.",
                "skills": [
                    "agile scrum practices",
                    "api testing using postman",
                    "automated tests using testng",
                    "cross-browser testing with browserstack",
                    "defect management via jira",
                    "functional, integration, and smoke testing",
                    "project builds with maven on mac, windows, ubuntu"
                ],
                "qualifications_summary": "B. Tech in Information Technology from Hindustan University-Chennai, Tamil Nadu (Not Found)",
                "experience_summary": "8 years of experience in software development. At Tata Cliq-Gurugram, Haryana, developed and implemented automation scripts for regression, smoke, and functional testing. At Times Internet-Gurugram, Haryana, performed API testing using Postman, designed test cases for mobile and web applications, and collaborated closely with developers for bug identification and resolution. At Appster-Gurugram, Haryana, created and executed test cases for functional and regression testing, provided detailed test reports and defect analysis to stakeholders, and performed end-to-end manual testing for web and mobile applications across multiple modules.",
                "companies_worked_with_duration": [
                    "Tata Cliq (January 2020 - December 2024)",
                    "Times Internet (January 2019 - September 2019)",
                    "Appster (November 2017 - December 2018)",
                    "Goibibo (September 2015 - October 2017)"
                ],
                "certifications": ["Not Found"],
                "awards_achievements": ["Not Found"],
                "projects": [
                    "E-commerce Backend Service: Developed REST APIs us…",
                    "AI Chatbot: Built conversational AI using Rasa and…"
                ],
                "languages": ["English (Native)"],
                "availability_status": "Immediately available",
                "work_authorization_status": None,
                "has_photo": False,
                "_original_filename": "ResumeMadhavKumar.pdf",
                "personal_details": None,
                "personal_info": None,
                "_is_master_record": True,
                "_duplicate_group_id": "4a329220-901e-427e-83e2-a6a48db7c3b8",
                "_duplicate_count": 1,
                "_associated_original_filenames": ["ResumeMadhavKumar.pdf"],
                "_associated_ids": ["ResumeMadhavKumar"]
            }
        ]
    
    def delete_resume_embedding(self, embedding_id: str, collection: str):
        """Delete resume embedding from vector database"""
        pass

vector_service = VectorService()