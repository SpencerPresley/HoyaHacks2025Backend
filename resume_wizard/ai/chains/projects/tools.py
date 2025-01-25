"""Tools for extracting project information from resumes."""
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from resume_wizard.ai_helpers.concrete_tools.res_parser import _ResumeParsingTools

class CoreProjectInput(BaseModel):
    """Input schema for core project details."""
    name: str = Field(
        description="Title of the project"
    )
    description: str = Field(
        description="Detailed explanation of the project and its impact"
    )
    url: Optional[str] = Field(
        None,
        description="Link to project repository or demo"
    )
    timeframe: Optional[str] = Field(
        None,
        description="Duration or completion date of the project"
    )

class ProjectDetailsInput(BaseModel):
    """Input schema for additional project details."""
    name: str = Field(
        description="Title of the project to update"
    )
    role: Optional[str] = Field(
        None,
        description="Individual's role or contribution to the project"
    )
    team_size: Optional[int] = Field(
        None,
        description="Number of team members involved"
    )
    status: Optional[str] = Field(
        None,
        description="Current status of the project (completed, ongoing, etc.)"
    )
    technologies: Optional[List[str]] = Field(
        None,
        description="Technical tools and technologies used in the project"
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="Key terms describing project features and outcomes"
    )

def create_project_tools(tools: Any) -> List[Dict[str, Any]]:
    """Create tools for extracting project information.
    
    Args:
        tools: The tools instance containing project-related methods
        
    Returns:
        List[Dict[str, Any]]: List of tool configurations for Claude
    """
    # Remove fields Claude doesn't expect
    core_schema = CoreProjectInput.model_json_schema()
    del core_schema["title"]
    del core_schema["description"]
    
    details_schema = ProjectDetailsInput.model_json_schema()
    del details_schema["title"]
    del details_schema["description"]
    
    return [
        {
            "type": "function",
            "function": {
                "name": "add_project",
                "description": "Add a new project entry with core details like name, description, URL, etc.",
                "parameters": core_schema
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_project_details",
                "description": "Add additional details to an existing project entry like technologies and keywords",
                "parameters": details_schema
            }
        }
    ] 