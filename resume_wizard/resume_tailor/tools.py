"""Tools for updating resume template data."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class UpdateContactInfo(BaseModel):
    """Tool for updating contact information."""
    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    linkedin: str = Field(description="LinkedIn URL")
    github: str = Field(description="GitHub URL")

class EducationEntry(BaseModel):
    """Model for education entries."""
    university: str = Field(description="University name")
    degree: str = Field(description="Degree name")
    major: str = Field(description="Major/field of study")
    gpa: float = Field(description="GPA (optional)", default=None)
    start_date: str = Field(description="Start date (MM/YYYY)")
    end_date: str = Field(description="End date (MM/YYYY or 'Present')")
    location: str = Field(description="Location (City, State)")

class UpdateEducation(BaseModel):
    """Tool for updating education section."""
    education: List[EducationEntry] = Field(description="List of education entries")

class ExperienceEntry(BaseModel):
    """Model for experience entries."""
    company: str = Field(description="Company name")
    title: str = Field(description="Job title")
    start_date: str = Field(description="Start date (MM/YYYY)")
    end_date: str = Field(description="End date (MM/YYYY or 'Present')")
    location: str = Field(description="Location (City, State)")
    bullets: List[str] = Field(description="List of bullet points describing achievements")

class UpdateExperience(BaseModel):
    """Tool for updating experience section."""
    experience: List[ExperienceEntry] = Field(description="List of experience entries")

class ProjectEntry(BaseModel):
    """Model for project entries."""
    name: str = Field(description="Project name")
    description: str = Field(description="Brief project description")
    technologies: List[str] = Field(description="List of technologies used")
    bullets: List[str] = Field(description="List of bullet points describing achievements")
    url: str = Field(description="Project URL (optional)", default=None)

class UpdateProjects(BaseModel):
    """Tool for updating projects section."""
    projects: List[ProjectEntry] = Field(description="List of project entries")

class UpdateSkills(BaseModel):
    """Tool for updating technical skills."""
    skills: Dict[str, List[str]] = Field(description="Dictionary mapping skill categories to lists of skills")

def create_tailoring_tools() -> List[Dict[str, Any]]:
    """Create tools for updating resume template data.
    
    Returns:
        List[Dict[str, Any]]: List of tool definitions
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "update_contact_info",
                "description": "Update contact information in the template",
                "parameters": UpdateContactInfo.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_education",
                "description": "Update education section in the template",
                "parameters": UpdateEducation.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_experience",
                "description": "Update experience section in the template",
                "parameters": UpdateExperience.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_projects",
                "description": "Update projects section in the template",
                "parameters": UpdateProjects.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_skills",
                "description": "Update technical skills in the template",
                "parameters": UpdateSkills.model_json_schema()
            }
        }
    ] 