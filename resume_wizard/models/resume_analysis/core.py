import random
from typing import (
    Optional, 
    List, 
    Dict, 
    Any, 
    Type,
    TYPE_CHECKING
)

from pydantic import BaseModel, Field, model_validator

from ._support import (
    _EducationSchema,
    _ExperienceSchema,
    _ProjectSchema,
    _SkillsSchema
)

class ResumeAnalysisSchema(BaseModel):
    """A class model for purposes of pulling information from a provided resume.
    
    Attributes:
        name (str): Full name of the candidate
        email (str): Professional email address
        phone (str): Contact phone number
        linkedin (str): LinkedIn profile URL
        github (str): GitHub profile URL
        objective (str): Career objective or professional summary
        education (List[_EducationSchema]): Educational background and qualifications
        experience (List[_ExperienceSchema]): Professional work experience
        skills (List[str]): List of professional skills and competencies
        projects (List[_ProjectSchema]): Notable projects and their details
        certifications (List[str]): Professional certifications and credentials
        languages (List[str]): Programming languages mentioned throughout the resume
    
    Methods:
        set_required_defaults: Sets default values for the required fields if not provided
        _generate_random_email: Generates a random email address
        _generate_random_phone: Generates a random phone number
        _generate_random_name: Generates a random name
    """
    # User-provided required fields.
    #
    # Generated in before in the event they're not provided
    # for testing purposes
    name: str = Field(
        None, 
        description="Full name of the candidate",
    )
    email: str = Field(
        None, 
        description="Professional email address",
    )
    phone: str = Field(
        None, 
        description="Contact phone number"
    )
    
    
    # Optional fields
    linkedin: Optional[str] = Field(
        None, 
        description="LinkedIn profile URL"
    )
    github: Optional[str] = Field(
        None, 
        description="GitHub profile URL"
    )
    objective: Optional[str] = Field(
        None, 
        description="Career objective or professional summary"
    )
    education: Optional[List[_EducationSchema]] = Field(
        None, 
        description="Educational background and qualifications"
    )
    experience: Optional[List[_ExperienceSchema]] = Field(
        None, 
        description="Professional work experience"
    )
    skills: Optional[_SkillsSchema] = Field(
        None, 
        description="List of professional skills and competencies"
    )
    projects: Optional[List[_ProjectSchema]] = Field(
        None, 
        description="Notable projects and their details"
    )
    languages: Optional[List[str]] = Field(
        None, 
        description="Programming languages mentioned throughout the resume"
    )