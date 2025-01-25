from typing import Type, Dict, List, Any, Optional
from pydantic import BaseModel
import random

from resume_wizard.models.resume_analysis._support import (
    _EducationSchema,
    _ExperienceSchema,
    _ProjectSchema,
    _SkillsSchema
)
from resume_wizard.models.resume_analysis.core import ResumeAnalysisSchema

class _ResumeParserHelper(BaseModel):
    """Helper class for managing resume data during parsing."""
    
    # Basic tracking
    user_int: int = 0
    
    # Storage for resume sections
    contact_info: Dict[str, str] = {}
    social_links: Dict[str, Optional[str]] = {"linkedin": None, "github": None}
    objective: Optional[str] = None
    
    # Complex sections
    education_entries: List[Dict[str, Any]] = []
    experience_entries: List[Dict[str, Any]] = []
    project_entries: List[Dict[str, Any]] = []
    skills: Dict[str, List[str]] = {
        "languages": [],
        "frameworks": [],
        "dev_tools": [],
        "databases": [],
        "libraries": [],
        "cloud_platforms": [],
        "methodologies": [],
        "soft_skills": [],
        "other": []
    }
    
    def generate_random_name(self) -> str:
        """Generate a random name.
        
        Returns:
            str: A random name
        """
        name = f"person_{self.user_int}"
        self._increment_user_int()
        return name
    
    def generate_random_email(self) -> str:
        """Generate a random email address.
        
        Returns:
            str: A random email address
        """
        return f"person_{random.randint(1000, 9999)}@example.com"
    
    def generate_random_phone(self) -> str:
        """Generate a random phone number.
        
        Returns:
            str: A random phone number
        """
        return f"{random.randint(1000000000, 9999999999)}"
    
    def add_education(self, entry: Dict[str, Any]) -> None:
        """Add a new education entry."""
        self.education_entries.append(entry)
        
    def add_education_details(self, institution: str, details: Dict[str, Any]) -> None:
        """Add details to an existing education entry."""
        for entry in self.education_entries:
            if entry["institution"] == institution:
                entry.update(details)
                break
                
    def add_experience(self, entry: Dict[str, Any]) -> None:
        """Add a new experience entry."""
        self.experience_entries.append(entry)
        
    def add_experience_details(
        self, 
        position: str, 
        company: str, 
        details: Dict[str, Any]
    ) -> None:
        """Add details to an existing experience entry."""
        for entry in self.experience_entries:
            if entry["position"] == position and entry["company"] == company:
                entry.update(details)
                break
                
    def add_project(self, entry: Dict[str, Any]) -> None:
        """Add a new project entry."""
        self.project_entries.append(entry)
        
    def add_project_details(self, name: str, details: Dict[str, Any]) -> None:
        """Add details to an existing project entry."""
        for entry in self.project_entries:
            if entry["name"] == name:
                entry.update(details)
                break
                
    def add_languages(self, languages: List[str]) -> None:
        """Add programming languages."""
        self.skills["languages"].extend(languages)
        
    def add_skills(self, skill_type: str, skills: List[str]) -> None:
        """Add skills of a specific type."""
        if skill_type in self.skills:
            self.skills[skill_type].extend(skills)
            
    def add_soft_skills(self, skills: List[str]) -> None:
        """Add soft skills."""
        self.skills["soft_skills"].extend(skills)
    
    def build_resume_schema(self) -> ResumeAnalysisSchema:
        """Construct the final ResumeAnalysisSchema from collected data.
        
        Returns:
            ResumeAnalysisSchema: The complete resume schema
        """
        # Convert education entries to schema objects
        education_schemas = [
            _EducationSchema(**entry)
            for entry in self.education_entries
        ]
        
        # Convert experience entries to schema objects
        experience_schemas = [
            _ExperienceSchema(**entry)
            for entry in self.experience_entries
        ]
        
        # Convert project entries to schema objects
        project_schemas = [
            _ProjectSchema(**entry)
            for entry in self.project_entries
        ]
        
        # Build skills schema
        skills_schema = _SkillsSchema(
            languages=self.skills["languages"],
            frameworks=self.skills["frameworks"],
            dev_tools=self.skills["dev_tools"],
            databases=self.skills["databases"],
            libraries=self.skills["libraries"],
            cloud_platforms=self.skills["cloud_platforms"],
            methodologies=self.skills["methodologies"],
            soft_skills=self.skills["soft_skills"],
            other=self.skills["other"]
        )
        
        # Construct and return the full schema
        return ResumeAnalysisSchema(
            name=self.contact_info.get("name"),
            email=self.contact_info.get("email"),
            phone=self.contact_info.get("phone"),
            linkedin=self.social_links.get("linkedin"),
            github=self.social_links.get("github"),
            objective=self.objective,
            education=education_schemas,
            experience=experience_schemas,
            skills=skills_schema,
            projects=project_schemas,
            languages=self.skills["languages"]  # Languages appear both in skills and at top level
        )
    
    @classmethod
    def _increment_user_int(cls: Type['_ResumeParserHelper']) -> None:
        """Increment the user_int."""
        cls.user_int += 1
