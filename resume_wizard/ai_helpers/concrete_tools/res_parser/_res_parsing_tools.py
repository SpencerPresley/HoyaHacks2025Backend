from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from ._parser_helper import _ResumeParserHelper
    from resume_wizard.models.resume_analysis.core import ResumeAnalysisSchema

class _ResumeParsingTools(BaseModel):
    """A class housing helper methods for parsing resumes.
    
    The class is a collections of methods to be made available to an LLM to act as 'tools' to populate the `ResumeAnalysisSchema` model during parsing of a resume.
    """
    def __init__(
        self,
        _parser_helper: _ResumeParserHelper
    ):
        self._parser_helper = _parser_helper
        super().__init__()

    def set_contact_info(
        self,
        name: str | None,
        email: str | None,
        phone: str | None,
    ) -> str:
        """Set basic contact information for the resume.
        
        Args:
            name (str | None): The name of the person on the resume.
            email (str | None): The email address of the person on the resume.
            phone (str | None): The phone number of the person on the resume.
            
        Returns:
            str: Confirmation message of what was set
        """
        self._parser_helper.contact_info = {
            "name": name or self._parser_helper.generate_random_name(),
            "email": email or self._parser_helper.generate_random_email(),
            "phone": phone or self._parser_helper.generate_random_phone(),
        }
        return f"Set contact info for {name}"

    def set_social_links(
        self,
        linkedin: str | None = None,
        github: str | None = None,
    ) -> str:
        """Set social media links for the resume.
        
        Args:
            linkedin (str | None): LinkedIn profile URL
            github (str | None): GitHub profile URL
            
        Returns:
            str: Confirmation message
        """
        self._parser_helper.social_links = {
            "linkedin": linkedin,
            "github": github
        }
        return "Set social media links"

    def set_objective(
        self,
        objective: str
    ) -> str:
        """Set the career objective or professional summary.
        
        Args:
            objective (str): Career objective or professional summary
            
        Returns:
            str: Confirmation message
        """
        self._parser_helper.objective = objective
        return "Set career objective"

    def add_education(
        self,
        institution: str,
        degree: str,
        location: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        gpa: float | None = None,
    ) -> str:
        """Add core education details to the resume.
        
        Args:
            institution (str): Name of the educational institution
            degree (str): Degree earned or pursued
            location (str | None): City and state/country
            start_date (str | None): Start date of education
            end_date (str | None): End date or expected graduation
            gpa (float | None): GPA on 4.0 scale
            
        Returns:
            str: Confirmation message
        """
        education_entry = {
            "institution": institution,
            "degree": degree,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "gpa": gpa
        }
        self._parser_helper.add_education(education_entry)
        return f"Added core education entry for {institution}"

    def add_education_details(
        self,
        institution: str,
        minors: List[str] | None = None,
        honors: List[str] | None = None,
        relevant_coursework: List[str] | None = None,
        description: str | None = None
    ) -> str:
        """Add additional education details to an existing education entry.
        
        Args:
            institution (str): Name of the institution (to match with existing entry)
            minors (List[str] | None): List of minor fields of study
            honors (List[str] | None): Academic honors and distinctions
            relevant_coursework (List[str] | None): Key relevant courses
            description (str | None): Additional details
            
        Returns:
            str: Confirmation message
        """
        details = {
            "minors": minors,
            "honors": honors,
            "relevant_coursework": relevant_coursework,
            "description": description
        }
        self._parser_helper.add_education_details(institution, details)
        return f"Added additional education details for {institution}"

    def add_experience(
        self,
        position: str,
        company: str,
        description: str,
        location: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        ongoing: bool = False,
    ) -> str:
        """Add core experience entry to the resume.
        
        Args:
            position (str): Job title or role
            company (str): Name of employer
            description (str): Detailed responsibilities
            location (str | None): City and state/country
            start_date (str | None): Start date
            end_date (str | None): End date
            ongoing (bool): Whether this is current position
            
        Returns:
            str: Confirmation message
        """
        experience_entry = {
            "position": position,
            "company": company,
            "description": description,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "ongoing": ongoing,
        }
        self._parser_helper.add_experience(experience_entry)
        return f"Added experience entry for {position} at {company}"

    def add_experience_details(
        self,
        position: str,
        company: str,
        type: str | None = None,
        industry: str | None = None,
        achievements: List[str] | None = None,
        keywords: List[str] | None = None,
        technologies: List[str] | None = None
    ) -> str:
        """Add additional details to an existing experience entry.
        
        Args:
            position (str): Position title (to match existing entry)
            company (str): Company name (to match existing entry)
            type (str | None): Position type (full-time, etc.)
            industry (str | None): Industry sector
            achievements (List[str] | None): Key accomplishments
            keywords (List[str] | None): Key terms
            technologies (List[str] | None): Tools and technologies
            
        Returns:
            str: Confirmation message
        """
        details = {
            "type": type,
            "industry": industry,
            "achievements": achievements,
            "keywords": keywords,
            "technologies": technologies
        }
        self._parser_helper.add_experience_details(position, company, details)
        return f"Added additional details for {position} at {company}"

    def add_project(
        self,
        name: str,
        description: str,
        url: str | None = None,
        timeframe: str | None = None,
    ) -> str:
        """Add core project details to the resume.
        
        Args:
            name (str): Project title
            description (str): Project details
            url (str | None): Project link
            timeframe (str | None): Duration/completion date
            
        Returns:
            str: Confirmation message
        """
        project_entry = {
            "name": name,
            "description": description,
            "url": url,
            "timeframe": timeframe,
        }
        self._parser_helper.add_project(project_entry)
        return f"Added project {name}"

    def add_project_details(
        self,
        name: str,
        role: str | None = None,
        team_size: int | None = None,
        status: str | None = None,
        technologies: List[str] | None = None,
        keywords: List[str] | None = None
    ) -> str:
        """Add additional details to an existing project entry.
        
        Args:
            name (str): Project name (to match existing entry)
            role (str | None): Individual's role
            team_size (int | None): Number of team members
            status (str | None): Project status
            technologies (List[str] | None): Tools used
            keywords (List[str] | None): Key terms
            
        Returns:
            str: Confirmation message
        """
        details = {
            "role": role,
            "team_size": team_size,
            "status": status,
            "technologies": technologies,
            "keywords": keywords
        }
        self._parser_helper.add_project_details(name, details)
        return f"Added additional details for project {name}"

    def add_programming_languages(
        self,
        languages: List[str]
    ) -> str:
        """Add programming languages mentioned in the resume.
        
        Args:
            languages (List[str]): List of programming languages
            
        Returns:
            str: Confirmation message
        """
        self._parser_helper.add_languages(languages)
        return f"Added programming languages: {', '.join(languages)}"

    def add_technical_skills(
        self,
        skill_type: str,
        skills: List[str]
    ) -> str:
        """Add technical skills by category.
        
        Args:
            skill_type (str): Type of skills (frameworks, dev_tools, databases, libraries, cloud_platforms, methodologies)
            skills (List[str]): List of skills in this category
            
        Returns:
            str: Confirmation message
        """
        self._parser_helper.add_skills(skill_type, skills)
        return f"Added {skill_type} skills: {', '.join(skills)}"

    def add_soft_skills(
        self,
        skills: List[str]
    ) -> str:
        """Add soft skills to the resume.
        
        Args:
            skills (List[str]): List of soft skills
            
        Returns:
            str: Confirmation message
        """
        self._parser_helper.add_soft_skills(skills)
        return f"Added soft skills: {', '.join(skills)}"

    def build_resume(self) -> str:
        """Build the final ResumeAnalysisSchema from all collected data.
        
        This should be called after all resume information has been added using the other tools.
        
        Returns:
            str: Confirmation message
        """
        _ = self._parser_helper.build_resume_schema()
        return "Built final resume schema from collected data"
    
    
    