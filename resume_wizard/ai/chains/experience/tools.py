"""Tools for extracting experience information from resumes."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CoreExperienceInput(BaseModel):
    """Input schema for core experience details."""
    position: str = Field(
        description="Job title or role"
    )
    company: str = Field(
        description="Name of the employer or organization"
    )
    description: str = Field(
        description="Initial description of responsibilities and achievements"
    )
    location: Optional[str] = Field(
        None,
        description="City and state/country of the workplace"
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date of employment"
    )
    end_date: Optional[str] = Field(
        None,
        description="End date of employment"
    )
    ongoing: Optional[bool] = Field(
        None,
        description="Whether this is a current position"
    )

class ExperienceDetailsInput(BaseModel):
    """Input schema for additional experience details."""
    position: str = Field(
        description="Position title (to match existing entry)"
    )
    company: str = Field(
        description="Company name (to match existing entry)"
    )
    type: Optional[str] = Field(
        None,
        description="Type of position (full-time, part-time, internship, etc.)"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector of the position"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of responsibilities and achievements"
    )
    achievements: Optional[List[str]] = Field(
        None,
        description="Quantifiable results and key accomplishments"
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="Key terms related to job responsibilities and skills"
    )
    technologies: Optional[List[str]] = Field(
        None,
        description="Technical tools and technologies used in the role"
    )

def create_experience_tools(tools: Any) -> List[Dict[str, Any]]:
    """Create tools for extracting experience information.
    
    Args:
        tools: The tools instance containing experience-related methods
        
    Returns:
        List[Dict[str, Any]]: List of tool configurations for Claude
    """
    # Remove fields Claude doesn't expect
    core_schema = CoreExperienceInput.model_json_schema()
    del core_schema["title"]
    del core_schema["description"]
    
    details_schema = ExperienceDetailsInput.model_json_schema()
    del details_schema["title"]
    del details_schema["description"]
    
    return [
        {
            "type": "function",
            "function": {
                "name": "add_experience",
                "description": "Add a new experience entry with core details like position, company, dates, etc.",
                "parameters": core_schema
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_experience_details",
                "description": "Add additional details to an existing experience entry like type, industry, description, achievements, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "string",
                            "description": "Position/title of the experience entry to update"
                        },
                        "company": {
                            "type": "string",
                            "description": "Company name of the experience entry to update"
                        },
                        **details_schema["properties"]
                    },
                    "required": ["position", "company"]
                }
            }
        }
    ] 