import logging
from datetime import datetime
from sqlalchemy.orm import Session
from celery import current_task

from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.resume import Resume
from app.services.document_parser import document_parser
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_resume_task(self, resume_id: int):
    """Process a resume: parse content and generate embeddings"""
    db = SessionLocal()
    
    try:
        # Update task status
        current_task.update_state(
            state="PROCESSING",
            meta={"progress": 0, "message": "Starting resume processing"}
        )
        
        # Get resume from database
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise Exception(f"Resume with ID {resume_id} not found")
        
        # Update resume status
        resume.processing_status = "processing"
        db.commit()
        
        # Update task progress
        current_task.update_state(
            state="PROCESSING",
            meta={"progress": 20, "message": "Parsing document"}
        )
        
        # Parse the resume
        parsing_result = document_parser.parse_resume(
            resume.file_path, 
            resume.file_type
        )
        
        if parsing_result.get("error"):
            raise Exception(f"Parsing error: {parsing_result['error']}")
        
        # Update task progress
        current_task.update_state(
            state="PROCESSING",
            meta={"progress": 50, "message": "Updating resume information"}
        )
        
        # Update resume with parsed information
        resume.raw_text = parsing_result["raw_text"]
        resume.processed_text = parsing_result["processed_text"]
        resume.candidate_name = parsing_result["candidate_info"]["name"]
        resume.candidate_email = parsing_result["candidate_info"]["email"]
        resume.candidate_phone = parsing_result["candidate_info"]["phone"]
        resume.skills = parsing_result["skills"]
        resume.experience_years = parsing_result["experience_years"]
        resume.job_role = parsing_result["job_role"]
        resume.job_role_confidence = parsing_result["job_role_confidence"]
        
        db.commit()
        
        # Update task progress
        current_task.update_state(
            state="PROCESSING",
            meta={"progress": 70, "message": "Generating embeddings"}
        )
        
        # Generate and store embeddings
        if resume.processed_text:
            embedding_id = vector_service.add_resume_embedding(
                resume_id=resume.id,
                text=resume.processed_text,
                job_role=resume.job_role or "General",
                metadata={
                    "candidate_name": resume.candidate_name,
                    "skills": resume.skills,
                    "experience_years": resume.experience_years
                }
            )
            
            if embedding_id:
                resume.embedding_id = embedding_id
                resume.embedding_collection = f"resumes_{(resume.job_role or 'general').lower()}"
            else:
                logger.warning(f"Failed to generate embedding for resume {resume_id}")
        
        # Update task progress
        current_task.update_state(
            state="PROCESSING",
            meta={"progress": 90, "message": "Finalizing"}
        )
        
        # Mark as completed
        resume.is_processed = True
        resume.processing_status = "completed"
        resume.processed_timestamp = datetime.utcnow()
        resume.error_message = None
        
        db.commit()
        
        # Final task update
        current_task.update_state(
            state="SUCCESS",
            meta={
                "progress": 100, 
                "message": "Resume processing completed successfully",
                "resume_id": resume_id,
                "candidate_name": resume.candidate_name,
                "job_role": resume.job_role
            }
        )
        
        return {
            "resume_id": resume_id,
            "status": "completed",
            "candidate_name": resume.candidate_name,
            "job_role": resume.job_role,
            "skills_count": len(resume.skills) if resume.skills else 0
        }
    
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {e}")
        
        # Update resume with error
        if 'resume' in locals():
            resume.processing_status = "failed"
            resume.error_message = str(e)
            resume.processed_timestamp = datetime.utcnow()
            db.commit()
        
        # Update task with error
        current_task.update_state(
            state="FAILURE",
            meta={
                "progress": 0,
                "message": f"Error processing resume: {str(e)}",
                "error": str(e)
            }
        )
        
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def batch_process_resumes_task(self, resume_ids: list):
    """Process multiple resumes in batch"""
    total_resumes = len(resume_ids)
    processed_count = 0
    failed_count = 0
    results = []
    
    try:
        current_task.update_state(
            state="PROCESSING",
            meta={
                "progress": 0,
                "message": f"Starting batch processing of {total_resumes} resumes",
                "total": total_resumes,
                "processed": 0,
                "failed": 0
            }
        )
        
        for i, resume_id in enumerate(resume_ids):
            try:
                # Process individual resume
                result = process_resume_task.apply(args=[resume_id])
                results.append({
                    "resume_id": resume_id,
                    "status": "success",
                    "result": result.get()
                })
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process resume {resume_id}: {e}")
                results.append({
                    "resume_id": resume_id,
                    "status": "failed",
                    "error": str(e)
                })
                failed_count += 1
            
            # Update progress
            progress = int((i + 1) / total_resumes * 100)
            current_task.update_state(
                state="PROCESSING",
                meta={
                    "progress": progress,
                    "message": f"Processed {i + 1}/{total_resumes} resumes",
                    "total": total_resumes,
                    "processed": processed_count,
                    "failed": failed_count
                }
            )
        
        # Final update
        current_task.update_state(
            state="SUCCESS",
            meta={
                "progress": 100,
                "message": f"Batch processing completed: {processed_count} successful, {failed_count} failed",
                "total": total_resumes,
                "processed": processed_count,
                "failed": failed_count,
                "results": results
            }
        )
        
        return {
            "total": total_resumes,
            "processed": processed_count,
            "failed": failed_count,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        current_task.update_state(
            state="FAILURE",
            meta={
                "progress": 0,
                "message": f"Batch processing failed: {str(e)}",
                "error": str(e)
            }
        )
        raise e


@celery_app.task
def cleanup_old_files_task():
    """Clean up old temporary files"""
    import os
    import time
    from app.config import settings
    
    try:
        upload_dir = settings.upload_dir
        if not os.path.exists(upload_dir):
            return {"message": "Upload directory does not exist"}
        
        current_time = time.time()
        deleted_count = 0
        
        # Delete files older than 7 days
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 7 * 24 * 3600:  # 7 days in seconds
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}")
        
        return {
            "message": f"Cleanup completed: {deleted_count} files deleted",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise e