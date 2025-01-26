"""Resume tailoring functionality."""
from pathlib import Path
from typing import Optional

from .models import LatexTemplateData
from .chain import create_tailoring_chain, tailor_resume
from .renderer import LatexTemplateRenderer

def tailor_and_render_resume(
    resume_text: str,
    job_description: str,
    template_data: Optional[LatexTemplateData],
    api_key: str,
    output_dir: str | Path,
    output_filename: str,
    template_path: Optional[str | Path] = None
) -> Path:
    """Tailor a resume to a job description and render it to PDF.
    
    Args:
        resume_text: Original resume content as text
        job_description: Target job description
        template_data: Optional template data. If None, will be generated from resume_text
        api_key: Anthropic API key for Claude
        output_dir: Directory to save the PDF in
        output_filename: Name for the output PDF file (without extension)
        template_path: Optional path to LaTeX template. If not provided, uses default template.
        
    Returns:
        Path: Path to the generated PDF file
    """
    # Use default template if none provided
    if template_path is None:
        template_path = Path(__file__).parent / "template" / "jake_resume.tex"
    
    # Create the tailoring chain
    chain = create_tailoring_chain(api_key)
    
    # If no template data provided, let Claude analyze the resume and create it
    if template_data is None:
        # We'll pass an empty message first to have Claude analyze the resume
        messages = [{
            "role": "user",
            "content": f"""Please analyze this resume and extract the information needed for our LaTeX template:

Resume Text:
{resume_text}

Please extract:
1. Contact information (name, email, phone, LinkedIn, GitHub)
2. Education details (university, location, degree, dates)
3. Work experience (title, company, location, dates, bullet points)
4. Projects (name, technologies, dates, bullet points)
5. Technical skills (languages, frameworks, tools, libraries)

Format the information according to our template structure."""
        }]
        
        response = chain.invoke(messages)
        # The chain's tools will populate the template data
    
    # Now tailor the resume content to the job description
    tailored_data = tailor_resume(chain, resume_text, job_description, template_data)
    
    # Create renderer and generate PDF
    renderer = LatexTemplateRenderer(template_path)
    pdf_path = renderer.render_to_pdf(tailored_data, output_dir, output_filename)
    
    return pdf_path

__all__ = [
    "LatexTemplateData",
    "LatexTemplateRenderer",
    "tailor_and_render_resume"
] 