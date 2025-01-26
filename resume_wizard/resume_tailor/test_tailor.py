"""Test script for resume tailoring functionality."""
import os
from pathlib import Path
from dotenv import load_dotenv

from resume_wizard.pdf_parsers import parse_single_pdf
from resume_wizard.resume_tailor import tailor_and_render_resume

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

# Job description for testing
JOB_DESCRIPTION = """
Jr. Software Development Engineer (SDE) - Amazon
Location: Arlington, VA (In-Person)

Job Description:
We are seeking a talented Jr. Software Development Engineer to join our team at Amazon. As a Jr. SDE, you will work on challenging problems, learn from experienced engineers, and contribute to building scalable software solutions.

Basic Qualifications:
- Currently enrolled in a Bachelor's or Master's degree program in Computer Science, Software Engineering, or related field
- Programming experience with at least one modern language such as Java, Python, C++, or JavaScript
- Understanding of computer science fundamentals including data structures, algorithms, and object-oriented programming
- Ability to work effectively in an Agile team environment
- Strong problem-solving skills and attention to detail

Preferred Qualifications:
- Experience with web services and RESTful APIs
- Familiarity with cloud platforms (AWS, Azure, or GCP)
- Knowledge of version control systems (Git)
- Experience with testing frameworks and CI/CD pipelines
- Strong communication and collaboration skills

Additional Requirements:
- Must be able to work in-person in Arlington, VA
- Willingness to learn and adapt to new technologies
- Passion for building customer-focused solutions

Amazon is an Equal Opportunity Employer
"""

def main():
    """Run the test script."""
    # Load resume - just use filename since get_absolute_path_to_resume handles the directory
    resume_text = parse_single_pdf("spencer-presley-resume.pdf")
    
    # Set up output path
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "tailored_resume.pdf"
    
    # Tailor and render resume
    tailor_and_render_resume(
        resume_text=resume_text,
        job_description=JOB_DESCRIPTION,
        template_data=None,  # Let Claude analyze the resume
        api_key=api_key,
        output_dir=output_dir,
        output_filename=output_file.name
    )
    
    print(f"Tailored resume saved to: {output_file}")

if __name__ == "__main__":
    main() 