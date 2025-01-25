from __future__ import annotations

import os
import json
from typing import TYPE_CHECKING
from dotenv import load_dotenv
from langchain_anthropic.chat_models import ChatAnthropic
from resume_wizard.ai.chains.contact_info.chain import extract_contact_info, create_contact_info_chain
from resume_wizard.ai.chains.objective.chain import extract_objective, create_objective_chain
from resume_wizard.ai.chains.skills.chain import extract_skills, create_skills_chain
from resume_wizard.ai.chains.education.chain import extract_education, create_education_chain
from resume_wizard.ai.chains.experience.chain import extract_experience, create_experience_chain
from resume_wizard.ai.chains.projects.chain import extract_projects, create_projects_chain
from resume_wizard.pdf_parsers import parse_single_pdf
from resume_wizard.ai.tools import _ResumeParsingTools, _ResumeParserHelper

if TYPE_CHECKING:
    from langchain.docstore.document import Document

# Rebuild the model at module level
_ResumeParsingTools.model_rebuild()

def run_resume_wizard(resume_file_name: str):
    document: Document = parse_single_pdf(resume_file_name)[0]

    load_dotenv()

    # Create helper and tools
    helper = _ResumeParserHelper()
    tools = _ResumeParsingTools(parser_helper=helper)

    # First extract contact info
    contact_chain = create_contact_info_chain(
        os.getenv("ANTHROPIC_API_KEY"),
        tools
    )

    print("\n=== Extracting Contact Info ===\n")
    conversation = extract_contact_info(contact_chain, document.page_content, tools)
    print("\nContact Info Conversation:\n")
    print(conversation)

    # Then extract objective using the same tools instance
    objective_chain = create_objective_chain(
        os.getenv("ANTHROPIC_API_KEY"),
        tools
    )

    print("\n=== Extracting Objective ===\n")
    conversation = extract_objective(objective_chain, document.page_content, tools)
    print("\nObjective Conversation:\n")
    print(conversation)

    # Then extract all skills
    skills_chain = create_skills_chain(
        os.getenv("ANTHROPIC_API_KEY"),
        tools
    )

    print("\n=== Extracting Skills ===\n")
    conversation = extract_skills(skills_chain, document.page_content, tools)
    print("\nSkills Conversation:\n")
    print(conversation)

    # Then extract education information
    education_chain = create_education_chain(
        os.getenv("ANTHROPIC_API_KEY"),
        tools
    )

    print("\n=== Extracting Education ===\n")
    conversation = extract_education(education_chain, document.page_content, tools)
    print("\nEducation Conversation:\n")
    print(conversation)

    # Then extract experience information
    experience_chain = create_experience_chain(
        os.getenv("ANTHROPIC_API_KEY"),
        tools
    )

    print("\n=== Extracting Experience ===\n")
    conversation = extract_experience(experience_chain, document.page_content, tools)
    print("\nExperience Conversation:\n")
    print(conversation)

    # Finally extract project information
    projects_chain = create_projects_chain(
        os.getenv("ANTHROPIC_API_KEY"),
        tools
    )

    print("\n=== Extracting Projects ===\n")
    conversation = extract_projects(projects_chain, document.page_content, tools)
    print("\nProjects Conversation:\n")
    print(conversation)

    # Build and print the final resume schema with all pieces
    print("\nFinal Resume Schema:\n")
    resume_data = tools.build_resume()
    print(json.dumps(resume_data.model_dump(), indent=2))

    return resume_data.model_dump()