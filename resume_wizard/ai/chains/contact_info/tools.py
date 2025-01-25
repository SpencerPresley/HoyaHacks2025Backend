"""Tools for extracting contact information from resumes."""
from typing import Optional, Dict, Any

from langchain_anthropic.chat_models import AnthropicTool
from pydantic import BaseModel, Field

from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

class ContactInfoInput(BaseModel):
    """Input schema for contact info extraction."""
    name: Optional[str] = Field(None, description="Full name found in the resume")
    email: Optional[str] = Field(None, description="Email address found in the resume")
    phone: Optional[str] = Field(None, description="Phone number found in the resume")

class SocialLinksInput(BaseModel):
    """Input schema for social links."""
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL found in the resume")
    github: Optional[str] = Field(None, description="GitHub profile URL found in the resume")

def create_contact_info_tools(parser_tools: _ResumeParsingTools) -> list[Dict[str, Any]]:
    """Create Claude-specific tools for contact info extraction.
    
    Args:
        parser_tools: The resume parsing tools instance
        
    Returns:
        list[Dict[str, Any]]: List of Claude-specific tools for contact info extraction
    """
    contact_schema = ContactInfoInput.model_json_schema()
    social_schema = SocialLinksInput.model_json_schema()
    
    # Remove schema elements that Claude doesn't expect
    for schema in [contact_schema, social_schema]:
        if "title" in schema:
            del schema["title"]
        if "$schema" in schema:
            del schema["$schema"]
        if "description" in schema:
            del schema["description"]
    
    return [
        {
            "name": "set_contact_info",
            "description": "Save the person's name, email, and phone number found in the resume",
            "input_schema": contact_schema
        },
        {
            "name": "set_social_links",
            "description": "Save the person's LinkedIn and GitHub URLs found in the resume",
            "input_schema": social_schema
        }
    ]