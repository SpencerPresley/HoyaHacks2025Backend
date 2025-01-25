"""Tools for extracting all skills from resumes."""
from typing import Optional, Dict, Any, List

from langchain_anthropic.chat_models import AnthropicTool
from pydantic import BaseModel, Field

from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

class LanguagesInput(BaseModel):
    """Input schema for languages extraction."""
    languages: List[str] = Field(..., description="List of programming languages found in the resume")

class TechnicalSkillsInput(BaseModel):
    """Input schema for technical skills extraction."""
    skill_type: str = Field(..., description="Type of skills (frameworks, dev_tools, databases, libraries, cloud_platforms, methodologies, other)")
    skills: List[str] = Field(..., description="List of skills in this category")

class SoftSkillsInput(BaseModel):
    """Input schema for soft skills extraction."""
    skills: List[str] = Field(..., description="List of soft skills found in the resume")

def create_skills_tools(parser_tools: _ResumeParsingTools) -> list[Dict[str, Any]]:
    """Create Claude-specific tools for skills extraction.
    
    Args:
        parser_tools: The resume parsing tools instance
        
    Returns:
        list[Dict[str, Any]]: List of Claude-specific tools for skills extraction
    """
    # Get schemas
    languages_schema = LanguagesInput.model_json_schema()
    technical_skills_schema = TechnicalSkillsInput.model_json_schema()
    soft_skills_schema = SoftSkillsInput.model_json_schema()
    
    # Remove schema elements that Claude doesn't expect
    for schema in [languages_schema, technical_skills_schema, soft_skills_schema]:
        if "title" in schema:
            del schema["title"]
        if "$schema" in schema:
            del schema["$schema"]
        if "description" in schema:
            del schema["description"]
    
    return [
        {
            "name": "add_programming_languages",
            "description": "Save programming languages found in the resume",
            "input_schema": languages_schema
        },
        {
            "name": "add_technical_skills",
            "description": "Save technical skills of a specific type (frameworks, dev_tools, databases, libraries, cloud_platforms, methodologies, other)",
            "input_schema": technical_skills_schema
        },
        {
            "name": "add_soft_skills",
            "description": "Save soft skills found in the resume",
            "input_schema": soft_skills_schema
        }
    ] 