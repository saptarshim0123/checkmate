import pdfplumber
import re
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


def is_image_only_pdf(text: Optional[str]) -> bool:
    """
    Detect if PDF is image-only (scanned/photographed) by checking extracted text.
    
    Args:
        text: Extracted text from PDF (can be None)
        
    Returns:
        True if PDF appears to be image-only, False otherwise
    """
    if text is None:
        return True
    
    text = text.strip()
    
    # If text is too short, likely image-only
    if len(text) < 100:
        return True
    
    # Count meaningful words (at least 3 characters)
    words = re.findall(r'\b\w{3,}\b', text)
    
    # If very few meaningful words, likely image-only
    if len(words) < 10:
        return True
    
    # Check if text contains mostly non-alphabetic characters (OCR artifacts)
    # Image-only PDFs often have poor OCR with lots of special characters
    alpha_chars = sum(1 for c in text if c.isalpha())
    total_chars = len([c for c in text if not c.isspace()])
    
    if total_chars > 0:
        alpha_ratio = alpha_chars / total_chars
        # If less than 40% alphabetic characters, likely image-only with poor OCR
        if alpha_ratio < 0.4:
            return True
    
    return False


def validate_pdf_content(text: str) -> bool:
    """
    Validate that extracted text is meaningful and from a text-based PDF.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        True if content seems valid, False otherwise
    """
    # Check if it's an image-only PDF first
    if is_image_only_pdf(text):
        return False
    
    # Basic validation: at least 50 characters
    if not text or len(text.strip()) < 50:
        return False
    
    # Check if it contains some common resume keywords
    resume_keywords = ['experience', 'education', 'skills', 'project', 'work', 'resume', 'cv', 'employment']
    text_lower = text.lower()
    
    # Check if any keyword from the list is present
    return any(keyword in text_lower for keyword in resume_keywords)