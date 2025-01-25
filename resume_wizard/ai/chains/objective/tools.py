"""Tools for extracting career objective from resumes."""
from typing import Optional, Dict, Any

from langchain_anthropic.chat_models import AnthropicTool
from pydantic import BaseModel, Field

from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

class ObjectiveInput(BaseModel):
    """Input schema for objective extraction."""
    objective: str = Field(..., description="Career objective or professional summary text found in the resume")

def create_objective_tools(parser_tools: _ResumeParsingTools) -> list[Dict[str, Any]]:
    """Create Claude-specific tools for objective extraction.
    
    Args:
        parser_tools: The resume parsing tools instance
        
    Returns:
        list[Dict[str, Any]]: List of Claude-specific tools for objective extraction
    """
    objective_schema = ObjectiveInput.model_json_schema()
    
    # Remove schema elements that Claude doesn't expect
    if "title" in objective_schema:
        del objective_schema["title"]
    if "$schema" in objective_schema:
        del objective_schema["$schema"]
    if "description" in objective_schema:
        del objective_schema["description"]
    
    return [
        {
            "name": "set_objective",
            "description": "Save the career objective or professional summary found in the resume",
            "input_schema": objective_schema
        }
    ] 