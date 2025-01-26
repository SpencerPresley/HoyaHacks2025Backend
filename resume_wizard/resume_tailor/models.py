"""Models for resume tailoring and LaTeX template data."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class EducationEntry(BaseModel):
    """Model for education entries in the LaTeX template."""
    university_name: Optional[str] = ""
    university_city: Optional[str] = ""
    university_state: Optional[str] = ""
    major_degree_name: Optional[str] = ""
    minor_degree_name: Optional[str] = None
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""

class ExperienceEntry(BaseModel):
    """Model for work experience entries in the LaTeX template."""
    work_title: Optional[str] = ""
    work_company: Optional[str] = ""
    work_city: Optional[str] = ""
    work_state: Optional[str] = ""
    work_start_date: Optional[str] = ""
    work_end_date: Optional[str] = ""
    work_descriptions: List[str] = Field(
        default_factory=list,
        description="List of bullet points describing work experience. Each item will be a \\resumeItem"
    )

class ProjectEntry(BaseModel):
    """Model for project entries in the LaTeX template."""
    project_name: Optional[str] = ""
    project_technologies: Optional[str] = Field(
        default="",
        description="Technologies used, formatted as a comma-separated string"
    )
    project_start_date: Optional[str] = ""
    project_end_date: Optional[str] = ""
    project_bullets: List[str] = Field(
        default_factory=list,
        description="List of bullet points describing the project. Each item will be a \\resumeItem"
    )

class TechnicalSkills(BaseModel):
    """Model for technical skills section in the LaTeX template."""
    languages: Optional[str] = Field(
        default="",
        description="Programming languages, formatted as a comma-separated string"
    )
    frameworks: Optional[str] = Field(
        default="",
        description="Frameworks and libraries, formatted as a comma-separated string"
    )
    dev_tools: Optional[str] = Field(
        default="",
        description="Developer tools, formatted as a comma-separated string"
    )
    libraries: Optional[str] = Field(
        default="",
        description="Additional libraries, formatted as a comma-separated string"
    )

class LatexTemplateData(BaseModel):
    """Complete model for all data needed in the LaTeX template."""
    # Contact Info
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = Field(default="", description="LinkedIn profile URL")
    github: Optional[str] = Field(default="", description="GitHub profile URL")

    # Main Sections
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    technical_skills: Optional[TechnicalSkills] = Field(
        default_factory=lambda: TechnicalSkills()
    ) 