from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pdf_parser import extract_text_from_pdf, validate_pdf_content, is_image_only_pdf
from llm_service import analyze_resume
import os

# Initialize FastAPI app
app = FastAPI(
    title="CheckMate - Resume Analyzer",
    description="AI-powered resume analysis against job descriptions",
    version="1.0.0"
)

# CORS Configuration - frontend to communicate
# Supports environment variable CORS_ORIGINS for production (comma-separated list)
# Defaults to ["*"] for development if not set
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    # Parse comma-separated origins from environment variable
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
else:
    # Development default: allow all origins
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "CheckMate API is running!",
        "status": "healthy",
        "endpoints": {
            "analyze": "/analyze - POST - Analyze resume against JD",
            "docs": "/docs - Interactive API documentation"
        }
    }


@app.post("/analyze")
async def analyze_resume_endpoint(
    resume: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = Form(..., description="Job description text")
):
    """
    Analyze resume against job description.
    
    Args:
        resume: PDF file of the resume
        job_description: Text of the job description
        
    Returns:
        JSON with match score, gaps, and improvements
    """
    
    # Validate file type
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a PDF resume."
        )
    
    # Validate job description
    if not job_description or len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please provide a detailed job description (at least 50 characters)."
        )
    
    try:
        # Step 1: Extract text from PDF
        resume_text = extract_text_from_pdf(resume)
        
        # Step 2: Check if PDF is image-only (scanned/photographed)
        if is_image_only_pdf(resume_text):
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF appears to be an image-only or scanned document. Please upload a text-based PDF resume. If you have a scanned PDF, consider using OCR software to convert it to a text-based PDF first."
            )
        
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. Please ensure the PDF contains readable text (not just images)."
            )
        
        # Step 3: Validate resume content
        if not validate_pdf_content(resume_text):
            raise HTTPException(
                status_code=400,
                detail="The PDF doesn't appear to be a valid resume. Please upload a proper text-based resume document with readable content."
            )
        
        # Step 4: Analyze using Gemini AI
        analysis_result = analyze_resume(resume_text, job_description.strip())
        
        # Step 5: Return results
        return {
            "success": True,
            "filename": resume.filename,
            "analysis": analysis_result
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during analysis: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Detailed health check for deployment monitoring"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "gemini_configured": os.getenv("GEMINI_API_KEY") is not None
    }