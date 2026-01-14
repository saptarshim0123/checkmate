import pdfplumber
from typing import Optional

def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: File object from FastAPI upload
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        text_content = ""
        
        # Open PDF with pdfplumber
        with pdfplumber.open(pdf_file.file) as pdf:
            # Extract text from each page
            for page in pdf.pages:
                page_txt = page.extract_text()
                if page_txt:
                    text_content += page_txt + "\n"
        
        if text_content.strip():
            return text_content.strip()
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting PDF: {str(e)}")
        return None


def validate_pdf_content(text: str) -> bool:
    """
    Validate that extracted text is meaningful.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        True if content seems valid, False otherwise
    """
    # Basic validation: at least 50 characters
    if not text or len(text.strip()) < 50:
        return False
    
    # Check if it contains some common resume keywords
    resume_keywords = ['experience', 'education', 'skills', 'project', 'work']
    text_lower = text.lower()
    
    # Check if any keyword from the list is  present
    return any(keyword in text_lower for keyword in resume_keywords)