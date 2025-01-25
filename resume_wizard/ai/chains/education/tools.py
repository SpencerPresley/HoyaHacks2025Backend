"""Tools for extracting education information from resumes."""
from typing import Optional, Dict, Any, List

from langchain_anthropic.chat_models import AnthropicTool
from pydantic import BaseModel, Field

from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

class CoreEducationInput(BaseModel):
    """Input schema for core education details."""
    institution: str = Field(..., description="Name of the educational institution")
    degree: str = Field(..., description="Degree earned or pursued")
    location: Optional[str] = Field(None, description="City and state/country")
    start_date: Optional[str] = Field(None, description="Start date of education")
    end_date: Optional[str] = Field(None, description="End date or expected graduation")
    gpa: Optional[float] = Field(None, description="GPA on 4.0 scale")

class EducationDetailsInput(BaseModel):
    """Input schema for additional education details."""
    institution: str = Field(..., description="Name of the institution (to match existing entry)")
    minors: Optional[List[str]] = Field(None, description="List of minor fields of study")
    honors: Optional[List[str]] = Field(None, description="Academic honors and distinctions")
    relevant_coursework: Optional[List[str]] = Field(None, description="Key relevant courses")
    description: Optional[str] = Field(None, description="Additional details about coursework, achievements, or activities")

def create_education_tools(parser_tools: _ResumeParsingTools) -> list[Dict[str, Any]]:
    """Create Claude-specific tools for education extraction.
    
    Args:
        parser_tools: The resume parsing tools instance
        
    Returns:
        list[Dict[str, Any]]: List of Claude-specific tools for education extraction
    """
    # Get schemas
    core_schema = CoreEducationInput.model_json_schema()
    details_schema = EducationDetailsInput.model_json_schema()
    
    # Remove schema elements that Claude doesn't expect
    for schema in [core_schema, details_schema]:
        if "title" in schema:
            del schema["title"]
        if "$schema" in schema:
            del schema["$schema"]
        if "description" in schema:
            del schema["description"]
    
    return [
        {
            "name": "add_education",
            "description": "Add core education details (institution, degree, dates, etc.)",
            "input_schema": core_schema
        },
        {
            "name": "add_education_details",
            "description": "Add additional education details (minors, honors, coursework, etc.)",
            "input_schema": details_schema
        }
    ] 