from __future__ import annotations

import os
import json
from typing import TYPE_CHECKING, Generator, Dict, Any
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
import sys
from io import StringIO
from contextlib import contextmanager

if TYPE_CHECKING:
    from langchain.docstore.document import Document

# Rebuild the model at module level
_ResumeParsingTools.model_rebuild()

def format_conversation(conversation: str) -> str:
    """Format the conversation to be more readable."""
    lines = conversation.split('\n')
    formatted_lines = []
    for line in lines:
        if line.startswith('Human:'):
            formatted_lines.append('\n🧑 User:')
            formatted_lines.append('  ' + line[7:].strip())
        elif line.startswith('Assistant:'):
            formatted_lines.append('\n🤖 Claude:')
            formatted_lines.append('  ' + line[11:].strip())
        elif line.startswith('Tool'):
            formatted_lines.append('\n🛠️ Tool Output:')
            formatted_lines.append('  ' + line[line.find(':')+1:].strip())
        elif line.strip():
            formatted_lines.append('  ' + line.strip())
    return '\n'.join(formatted_lines)

@contextmanager
def capture_output():
    """Capture stdout and stderr"""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def run_resume_wizard(resume_file_name: str, stream: bool = False) -> dict | Generator[str, None, None]:
    """Run the resume wizard on a PDF file.
    
    Args:
        resume_file_name: Name of the PDF file to process
        stream: If True, yield status updates as they happen
        
    Returns:
        If stream=False: The processed resume data as a dict
        If stream=True: A generator yielding status updates
    """
    document: Document = parse_single_pdf(resume_file_name)[0]
    load_dotenv()

    # Create helper and tools
    helper = _ResumeParserHelper()
    tools = _ResumeParsingTools(parser_helper=helper)

    sections = [
        ("Contact Info", create_contact_info_chain, extract_contact_info),
        ("Objective", create_objective_chain, extract_objective),
        ("Skills", create_skills_chain, extract_skills),
        ("Education", create_education_chain, extract_education),
        ("Experience", create_experience_chain, extract_experience),
        ("Projects", create_projects_chain, extract_projects)
    ]

    for section_name, create_chain, extract_func in sections:
        status = f"\n{'='*20} Processing {section_name} {'='*20}\n"
        if stream:
            yield status
        else:
            print(status)

        # Capture all output during chain creation and execution
        with capture_output() as (out, err):
            chain = create_chain(os.getenv("ANTHROPIC_API_KEY"), tools)
            conversation = extract_func(chain, document.page_content, tools)
            
            # Get any output that was captured
            stdout = out.getvalue()
            stderr = err.getvalue()
            
            if stream and (stdout or stderr):
                yield stdout
                if stderr:
                    yield stderr

        formatted = format_conversation(conversation)
        if stream:
            yield formatted + "\n"
        else:
            print(formatted)

    # Build the final resume schema
    with capture_output() as (out, err):
        resume_data = tools.build_resume()
        stdout = out.getvalue()
        stderr = err.getvalue()
        
        if stream and (stdout or stderr):
            yield stdout
            if stderr:
                yield stderr

    final_status = "\n✨ Final Resume Data:\n"
    if stream:
        yield final_status
        yield json.dumps(resume_data.model_dump(), indent=2)
    else:
        print(final_status)
        print(json.dumps(resume_data.model_dump(), indent=2))

    if not stream:
        return resume_data.model_dump()