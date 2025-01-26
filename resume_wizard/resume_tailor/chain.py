"""Chain for tailoring resumes to job descriptions."""
from typing import Dict, Any, List, Optional
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage

from .models import LatexTemplateData, EducationEntry, ExperienceEntry, ProjectEntry, TechnicalSkills
from .tools import create_tailoring_tools

ANALYSIS_PROMPT = """You are an expert at analyzing resumes and extracting structured information. Your task is to analyze a resume and extract information in a format suitable for our LaTeX template.

Guidelines for analysis:
1. Extract all relevant information from the resume text
2. Format information according to template requirements
3. Ensure dates are consistently formatted
4. Extract bullet points for experience and projects
5. Categorize skills appropriately

Process:
1. First analyze the resume to identify:
   - Contact information and social links
   - Education history
   - Work experience
   - Projects
   - Technical skills

2. Then use the provided tools to:
   - Format and save contact information
   - Structure education entries
   - Format work experience descriptions
   - Format project descriptions
   - Categorize technical skills

Important: After processing each section, verify that all required fields are populated and formatted correctly."""

TAILORING_PROMPT = """You are an expert resume writer and career coach. Your task is to tailor a resume to a specific job description, ensuring the content is optimized for both human readers and ATS systems.

Guidelines for tailoring:
1. Analyze both the resume and job description carefully
2. Identify key requirements and skills from the job description
3. Prioritize relevant experience and achievements
4. Use similar keywords and terminology as the job description
5. Quantify achievements where possible
6. Keep bullet points concise and impactful
7. Ensure all content fits the template format
8. Maintain professional tone and active voice

Process:
1. First analyze the job description to identify:
   - Required skills and technologies
   - Key responsibilities
   - Preferred qualifications
   - Industry-specific terminology

2. Then review the resume content and:
   - Highlight matching qualifications
   - Rewrite bullet points to emphasize relevant experience
   - Add quantifiable metrics where possible
   - Incorporate key terms from the job description
   - Remove or de-emphasize less relevant content

3. Format the content to fit the template:
   - Organize sections according to template structure
   - Ensure bullet points are clear and concise
   - Verify all dates and locations are properly formatted
   - Check that skills are correctly categorized

Important: After processing each section, provide a brief explanation of the changes made and how they align with the job requirements."""

def create_tailoring_chain(api_key: str):
    """Create a chain for analyzing and tailoring resumes.
    
    Args:
        api_key: Anthropic API key
        
    Returns:
        Chain: The configured chain
    """
    # Initialize Claude
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=api_key,
        max_tokens=4096
    )
    
    # Create tools
    tools = create_tailoring_tools()
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    return llm_with_tools

def analyze_resume(
    chain: Any,
    resume_text: str
) -> LatexTemplateData:
    """Analyze a resume and create template data.
    
    Args:
        chain: The analysis chain
        resume_text: Resume content to analyze
        
    Returns:
        LatexTemplateData: Extracted template data
    """
    print("\n=== Starting Resume Analysis ===")
    
    # Add system message for analysis
    chain = chain.with_config({
        "system_message": SystemMessage(content=ANALYSIS_PROMPT)
    })
    
    messages = [{
        "role": "user",
        "content": f"""Please analyze this resume and extract information for our template:

{resume_text}"""
    }]
    
    template_data = LatexTemplateData()  # Start with empty template
    print("\nCreated empty template data")
    
    while True:
        print("\nSending request to Claude...")
        response = chain.invoke(messages)
        print("Received response from Claude")
        
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # If no more tool calls, we're done
        if response.response_metadata.get('stop_reason') != "tool_use":
            print("No more tool calls, analysis complete")
            break
            
        # Get all tool use blocks
        tool_uses = [block for block in response.content if block.get('type') == "tool_use"]
        print(f"\nProcessing {len(tool_uses)} tool calls")
        
        # Process each tool use
        for tool_use in tool_uses:
            tool_name = tool_use['name']
            tool_args = tool_use['input']
            print(f"\nProcessing tool: {tool_name}")
            print(f"Tool arguments: {tool_args}")
            
            try:
                # Execute the tool and update template data
                if tool_name == "update_contact_info":
                    template_data.name = tool_args.get('name', template_data.name)
                    template_data.email = tool_args.get('email', template_data.email)
                    template_data.phone = tool_args.get('phone', template_data.phone)
                    template_data.linkedin = tool_args.get('linkedin', template_data.linkedin)
                    template_data.github = tool_args.get('github', template_data.github)
                    result = "Updated contact information"
                    
                elif tool_name == "update_education":
                    # Convert each education entry to proper model
                    education_entries = []
                    for entry in tool_args.get('education', []):
                        edu_entry = EducationEntry(
                            university_name=entry.get('university', ''),
                            university_city=entry.get('city', ''),
                            university_state=entry.get('state', ''),
                            major_degree_name=entry.get('degree', ''),
                            minor_degree_name=entry.get('minor', None),
                            start_date=entry.get('start_date', ''),
                            end_date=entry.get('end_date', '')
                        )
                        education_entries.append(edu_entry)
                    template_data.education = education_entries
                    result = f"Updated education section with {len(education_entries)} entries"
                    
                elif tool_name == "update_experience":
                    # Convert each experience entry to proper model
                    experience_entries = []
                    for entry in tool_args.get('experience', []):
                        exp_entry = ExperienceEntry(
                            work_title=entry.get('title', ''),
                            work_company=entry.get('company', ''),
                            work_city=entry.get('city', ''),
                            work_state=entry.get('state', ''),
                            work_start_date=entry.get('start_date', ''),
                            work_end_date=entry.get('end_date', ''),
                            work_descriptions=entry.get('bullets', [])
                        )
                        experience_entries.append(exp_entry)
                    template_data.experience = experience_entries
                    result = f"Updated experience section with {len(experience_entries)} entries"
                    
                elif tool_name == "update_projects":
                    # Convert each project entry to proper model
                    project_entries = []
                    for entry in tool_args.get('projects', []):
                        technologies = entry.get('technologies', [])
                        # Convert technologies list to string if needed
                        if isinstance(technologies, list):
                            technologies = ', '.join(technologies)
                            
                        proj_entry = ProjectEntry(
                            project_name=entry.get('name', ''),
                            project_technologies=technologies,
                            project_start_date=entry.get('start_date', ''),
                            project_end_date=entry.get('end_date', ''),
                            project_bullets=entry.get('bullets', [])
                        )
                        project_entries.append(proj_entry)
                    template_data.projects = project_entries
                    result = f"Updated projects section with {len(project_entries)} entries"
                    
                elif tool_name == "update_skills":
                    # Convert skills to proper model
                    skills = tool_args.get('skills', {})
                    template_data.technical_skills = TechnicalSkills(
                        languages=', '.join(skills.get('Languages', [])),
                        frameworks=', '.join(skills.get('Frameworks', [])),
                        dev_tools=', '.join(skills.get('Tools', [])),
                        libraries=', '.join(skills.get('Libraries', []))
                    )
                    result = "Updated technical skills"
                    
                else:
                    result = f"Unknown tool: {tool_name}"
                
                print(f"Tool result: {result}")
                
            except Exception as e:
                print(f"Error processing tool {tool_name}: {str(e)}")
                result = f"Error: {str(e)}"
            
            # Add tool result to messages
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use['id'],
                    "content": result
                }]
            })
    
    print("\n=== Resume Analysis Complete ===")
    print(f"Final template data: {template_data.model_dump_json(indent=2)}")
    return template_data

def tailor_resume(
    chain: Any,
    resume_text: str,
    job_description: str,
    template_data: Optional[LatexTemplateData] = None
) -> LatexTemplateData:
    """Tailor a resume to a job description.
    
    Args:
        chain: The tailoring chain
        resume_text: Original resume content
        job_description: Target job description
        template_data: Optional existing template data. If None, will analyze resume first.
        
    Returns:
        LatexTemplateData: Updated template data
    """
    print("\n=== Starting Resume Tailoring ===")
    
    # If no template data provided, analyze the resume first
    if template_data is None:
        print("\nNo template data provided, analyzing resume first...")
        template_data = analyze_resume(chain, resume_text)
    
    # Add system message for tailoring
    chain = chain.with_config({
        "system_message": SystemMessage(content=TAILORING_PROMPT)
    })
    
    messages = [{
        "role": "user",
        "content": f"""Please tailor this resume to the following job description:

Job Description:
{job_description}

Resume:
{resume_text}

Current Template Data:
{template_data.model_dump_json(indent=2)}

Please analyze both and update the template data to better match the job requirements."""
    }]
    
    print("\nStarting tailoring process...")
    while True:
        print("\nSending request to Claude...")
        response = chain.invoke(messages)
        print("Received response from Claude")
        
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # If no more tool calls, we're done
        if response.response_metadata.get('stop_reason') != "tool_use":
            print("No more tool calls, tailoring complete")
            break
            
        # Get all tool use blocks
        tool_uses = [block for block in response.content if block.get('type') == "tool_use"]
        print(f"\nProcessing {len(tool_uses)} tool calls")
        
        # Process each tool use
        for tool_use in tool_uses:
            tool_name = tool_use['name']
            tool_args = tool_use['input']
            print(f"\nProcessing tool: {tool_name}")
            print(f"Tool arguments: {tool_args}")
            
            try:
                # Execute the tool and update template data
                if tool_name == "update_contact_info":
                    template_data.name = tool_args.get('name', template_data.name)
                    template_data.email = tool_args.get('email', template_data.email)
                    template_data.phone = tool_args.get('phone', template_data.phone)
                    template_data.linkedin = tool_args.get('linkedin', template_data.linkedin)
                    template_data.github = tool_args.get('github', template_data.github)
                    result = "Updated contact information"
                    
                elif tool_name == "update_education":
                    # Convert each education entry to proper model
                    education_entries = []
                    for entry in tool_args.get('education', []):
                        edu_entry = EducationEntry(
                            university_name=entry.get('university', ''),
                            university_city=entry.get('city', ''),
                            university_state=entry.get('state', ''),
                            major_degree_name=entry.get('degree', ''),
                            minor_degree_name=entry.get('minor', None),
                            start_date=entry.get('start_date', ''),
                            end_date=entry.get('end_date', '')
                        )
                        education_entries.append(edu_entry)
                    template_data.education = education_entries
                    result = f"Updated education section with {len(education_entries)} entries"
                    
                elif tool_name == "update_experience":
                    # Convert each experience entry to proper model
                    experience_entries = []
                    for entry in tool_args.get('experience', []):
                        exp_entry = ExperienceEntry(
                            work_title=entry.get('title', ''),
                            work_company=entry.get('company', ''),
                            work_city=entry.get('city', ''),
                            work_state=entry.get('state', ''),
                            work_start_date=entry.get('start_date', ''),
                            work_end_date=entry.get('end_date', ''),
                            work_descriptions=entry.get('bullets', [])
                        )
                        experience_entries.append(exp_entry)
                    template_data.experience = experience_entries
                    result = f"Updated experience section with {len(experience_entries)} entries"
                    
                elif tool_name == "update_projects":
                    # Convert each project entry to proper model
                    project_entries = []
                    for entry in tool_args.get('projects', []):
                        technologies = entry.get('technologies', [])
                        # Convert technologies list to string if needed
                        if isinstance(technologies, list):
                            technologies = ', '.join(technologies)
                            
                        proj_entry = ProjectEntry(
                            project_name=entry.get('name', ''),
                            project_technologies=technologies,
                            project_start_date=entry.get('start_date', ''),
                            project_end_date=entry.get('end_date', ''),
                            project_bullets=entry.get('bullets', [])
                        )
                        project_entries.append(proj_entry)
                    template_data.projects = project_entries
                    result = f"Updated projects section with {len(project_entries)} entries"
                    
                elif tool_name == "update_skills":
                    # Convert skills to proper model
                    skills = tool_args.get('skills', {})
                    template_data.technical_skills = TechnicalSkills(
                        languages=', '.join(skills.get('Languages', [])),
                        frameworks=', '.join(skills.get('Frameworks', [])),
                        dev_tools=', '.join(skills.get('Tools', [])),
                        libraries=', '.join(skills.get('Libraries', []))
                    )
                    result = "Updated technical skills"
                    
                else:
                    result = f"Unknown tool: {tool_name}"
                
                print(f"Tool result: {result}")
                
            except Exception as e:
                print(f"Error processing tool {tool_name}: {str(e)}")
                result = f"Error: {str(e)}"
            
            # Add tool result to messages
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use['id'],
                    "content": result
                }]
            })
    
    print("\n=== Resume Tailoring Complete ===")
    print(f"Final template data: {template_data.model_dump_json(indent=2)}")
    return template_data 