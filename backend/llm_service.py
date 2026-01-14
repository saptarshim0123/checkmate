from google import genai
import os
import json
import re
from dotenv import load_dotenv
from typing import Dict, Any, Tuple

# Load environment variables
load_dotenv()

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Required keys for JSON response validation
REQUIRED_JSON_KEYS = ["match_score", "technical_gap", "soft_skills_gap", "improved_bullet_points"]


def validate_json_structure(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that the JSON response contains all required keys with correct types.
    
    Args:
        data: Parsed JSON dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for required keys
    missing_keys = [key for key in REQUIRED_JSON_KEYS if key not in data]
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    # Validate match_score is integer between 0-100
    if not isinstance(data["match_score"], int) or not (0 <= data["match_score"] <= 100):
        return False, "match_score must be an integer between 0 and 100"
    
    # Validate arrays are lists
    for key in ["technical_gap", "soft_skills_gap", "improved_bullet_points"]:
        if not isinstance(data[key], list):
            return False, f"{key} must be an array/list"
    
    return True, ""


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON from text, handling markdown code blocks and extra whitespace.
    
    Args:
        text: Raw text response from LLM
        
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object boundaries
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0).strip()
    
    return text.strip()


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Analyze resume against job description using Gemini AI.
    
    Args:
        resume_text: Extracted text from resume PDF
        job_description: Job description text
        
    Returns:
        Dictionary with analysis results
    """
    
    # Enhanced prompt with strict JSON enforcement
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and career coach. Analyze the following resume against the job description.

**RESUME:**
{resume_text}

**JOB DESCRIPTION:**
{job_description}

**INSTRUCTIONS:**
1. Calculate a match score (0-100) based on skills, experience, and requirements alignment
2. Identify technical skills gaps (skills in JD but missing in resume)
3. Identify soft skills gaps
4. Suggest 3-5 improved bullet points for the resume that better match the JD

**CRITICAL - JSON FORMAT REQUIREMENT:**
You MUST respond ONLY with valid JSON. No markdown, no explanations, no code blocks, no text before or after.
The response must be valid JSON that can be parsed directly.

Required JSON structure (all fields are mandatory):
{{
    "match_score": <integer between 0-100>,
    "technical_gap": ["skill1", "skill2", ...],
    "soft_skills_gap": ["skill1", "skill2", ...],
    "improved_bullet_points": [
        "Improved point 1",
        "Improved point 2",
        "Improved point 3"
    ],
    "summary": "Brief 2-3 sentence summary of overall fit"
}}

Remember: Respond ONLY with the JSON object. Nothing else.
"""
    
    try:
        # Generate response using the new client API
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",  # Using latest model
            contents=prompt
        )
        
        # Extract text from response
        response_text = response.text.strip()
        
        # Extract and clean JSON from response
        json_text = extract_json_from_text(response_text)
        
        # Parse JSON
        result = json.loads(json_text)
        
        # Validate JSON structure
        is_valid, error_msg = validate_json_structure(result)
        if not is_valid:
            print(f"JSON validation error: {error_msg}")
            print(f"Response was: {response_text}")
            raise ValueError(f"Invalid JSON structure: {error_msg}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Response was: {response_text}")
        # Return a default structure if parsing fails
        return {
            "match_score": 0,
            "technical_gap": ["Unable to analyze"],
            "soft_skills_gap": ["Unable to analyze"],
            "improved_bullet_points": ["Error in analysis. Please try again."],
            "summary": "Analysis failed due to response formatting error."
        }
        
    except ValueError as e:
        print(f"JSON validation error: {str(e)}")
        print(f"Response was: {response_text}")
        # Return a default structure if validation fails
        return {
            "match_score": 0,
            "technical_gap": ["Unable to analyze"],
            "soft_skills_gap": ["Unable to analyze"],
            "improved_bullet_points": ["Error in analysis. Please try again."],
            "summary": f"Analysis failed: {str(e)}"
        }
        
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return {
            "match_score": 0,
            "technical_gap": ["Error occurred"],
            "soft_skills_gap": ["Error occurred"],
            "improved_bullet_points": ["An error occurred during analysis."],
            "summary": f"Error: {str(e)}"
        }


def test_gemini_connection() -> bool:
    """
    Test if Gemini API is properly configured.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Say 'Hello' in JSON format: {\"message\": \"Hello\"}"
        )
        print(f"Test response: {response.text}")
        return True
    except Exception as e:
        print(f"Gemini connection failed: {str(e)}")
        return False