from typing import Optional, List
from pydantic import BaseModel, Field

class _EducationSchema(BaseModel):
    institution: Optional[str] = Field(
        None,
        description="Name of the educational institution attended"
    )
    location: Optional[str] = Field(
        None, 
        description="City and state/country of the institution"
    )
    degree: Optional[str] = Field(
        None, 
        description="Degree earned or pursued (e.g. Bachelor of Science in Computer Science)"
    )
    minors: Optional[List[str]] = Field(
        None, 
        description="List of minor fields of study"
    )
    start_date: Optional[str] = Field(
        None, 
        description="Start date of education period (e.g. 'Sept 2019')"
    )
    end_date: Optional[str] = Field(
        None, 
        description="End date or expected graduation date"
    )
    gpa: Optional[float] = Field(
        None, 
        description="Grade Point Average on a 4.0 scale"
    )
    honors: Optional[List[str]] = Field(
        None, 
        description="Academic honors and distinctions"
    )
    relevant_coursework: Optional[List[str]] = Field(
        None, 
        description="Key courses relevant to career goals"
    )
    description: Optional[str] = Field(
        None, 
        description="Additional details about coursework, achievements, or activities"
    )

class _ExperienceSchema(BaseModel):
    position: Optional[str] = Field(
        None, 
        description="Job title or role"
    )
    company: Optional[str] = Field(
        None, 
        description="Name of the employer or organization"
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
    position_type: Optional[str] = Field(
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
    
class _ProjectSchema(BaseModel):
    name: Optional[str] = Field(
        None, 
        description="Title of the project"
    )
    description: Optional[str] = Field(
        None, 
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
    
class _SkillsSchema(BaseModel):
    languages: Optional[List[str]] = Field(
        None, 
        description="Programming languages known"
    )
    frameworks: Optional[List[str]] = Field(
        None, 
        description="Software frameworks and platforms"
    )
    dev_tools: Optional[List[str]] = Field(
        None, 
        description="Development tools and environments"
    )
    databases: Optional[List[str]] = Field(
        None, 
        description="Database systems and technologies"
    )
    libraries: Optional[List[str]] = Field(
        None, 
        description="Software libraries and packages"
    )
    cloud_platforms: Optional[List[str]] = Field(
        None, 
        description="Cloud services and platforms"
    )
    methodologies: Optional[List[str]] = Field(
        None, 
        description="Development methodologies and practices"
    )
    soft_skills: Optional[List[str]] = Field(
        None, 
        description="Non-technical professional skills"
    )
    other: Optional[List[str]] = Field(
        None, 
        description="Other technical skills and competencies"
    )

class _SocialLinksSchema(BaseModel):
    """Schema for social media links."""
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")

class _ContactInfoSchema(BaseModel):
    """Schema for contact information."""
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(None, description="Phone number (if available)")
    social_links: Optional[_SocialLinksSchema] = Field(None, description="Social media profile links")

