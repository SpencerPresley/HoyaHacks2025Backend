"""LaTeX template renderer for resume tailoring."""
from pathlib import Path
import subprocess
from typing import Generator, Union
from .models import LatexTemplateData

class LatexTemplateRenderer:
    """Renders LaTeX templates with provided data."""
    
    def __init__(self, template_path: str | Path):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found at {template_path}")
            
        # Read the template
        with open(self.template_path) as f:
            self.template = f.read()
            
    def render(self, data: LatexTemplateData) -> str:
        """Render the template with the given data."""
        content = self.template
        
        # Contact info
        content = content.replace("{name}", str(data.name))
        content = content.replace("{email}", str(data.email))
        content = content.replace("{phone}", str(data.phone))
        content = content.replace("{linkedin}", str(data.linkedin))
        content = content.replace("{github}", str(data.github))
        
        # Education
        if data.education:
            content = content.replace("{university_name1}", str(data.education[0].university_name))
            content = content.replace("{university_city1}", str(data.education[0].university_city))
            content = content.replace("{university_state1}", str(data.education[0].university_state))
            content = content.replace("{major_degree_name1}", str(data.education[0].major_degree_name))
            content = content.replace("{minor_degree_name1}", str(data.education[0].minor_degree_name or ''))
            content = content.replace("{start_date1}", str(data.education[0].start_date))
            content = content.replace("{end_date1}", str(data.education[0].end_date))
            
        # Experience
        if data.experience:
            # First position
            content = content.replace("{work_title1}", str(data.experience[0].work_title))
            content = content.replace("{work_company1}", str(data.experience[0].work_company))
            content = content.replace("{work_city1}", str(data.experience[0].work_city))
            content = content.replace("{work_state1}", str(data.experience[0].work_state))
            content = content.replace("{work_start_date1}", str(data.experience[0].work_start_date))
            content = content.replace("{work_end_date1}", str(data.experience[0].work_end_date))
            for i, desc in enumerate(data.experience[0].work_descriptions[:3], 1):
                content = content.replace("{work_description_one" + str(i) + "}", str(desc))
                
            # Second position
            if len(data.experience) > 1:
                content = content.replace("{work_title2}", str(data.experience[1].work_title))
                content = content.replace("{work_company2}", str(data.experience[1].work_company))
                content = content.replace("{work_city2}", str(data.experience[1].work_city))
                content = content.replace("{work_state2}", str(data.experience[1].work_state))
                content = content.replace("{work_start_date2}", str(data.experience[1].work_start_date))
                content = content.replace("{work_end_date2}", str(data.experience[1].work_end_date))
                for i, desc in enumerate(data.experience[1].work_descriptions[:3], 1):
                    content = content.replace("{work_description_two" + str(i) + "}", str(desc))
                    
            # Third position
            if len(data.experience) > 2:
                content = content.replace("{work_title3}", str(data.experience[2].work_title))
                content = content.replace("{work_company3}", str(data.experience[2].work_company))
                content = content.replace("{work_city3}", str(data.experience[2].work_city))
                content = content.replace("{work_state3}", str(data.experience[2].work_state))
                content = content.replace("{work_start_date3}", str(data.experience[2].work_start_date))
                content = content.replace("{work_end_date3}", str(data.experience[2].work_end_date))
                for i, desc in enumerate(data.experience[2].work_descriptions[:6], 1):
                    content = content.replace("{work_description_three" + str(i) + "}", str(desc))
                    
        # Projects
        if data.projects:
            # First project
            content = content.replace("{project_1_name}", str(data.projects[0].project_name))
            content = content.replace("{project_1_technologies}", str(data.projects[0].project_technologies))
            content = content.replace("{project1_start_date}", str(data.projects[0].project_start_date))
            content = content.replace("{project1_end_date}", str(data.projects[0].project_end_date))
            for i, bullet in enumerate(data.projects[0].project_bullets[:4], 1):
                content = content.replace("{p1_bullet" + str(i) + "}", str(bullet))
                
            # Second project
            if len(data.projects) > 1:
                content = content.replace("{project_2_name}", str(data.projects[1].project_name))
                content = content.replace("{project_2_technologies}", str(data.projects[1].project_technologies))
                content = content.replace("{project2_start_date}", str(data.projects[1].project_start_date))
                content = content.replace("{project2_end_date}", str(data.projects[1].project_end_date))
                for i, bullet in enumerate(data.projects[1].project_bullets[:4], 1):
                    content = content.replace("{p2_bullet" + str(i) + "}", str(bullet))
                    
        # Technical Skills
        if data.technical_skills:
            content = content.replace("{language_names}", str(data.technical_skills.languages))
            content = content.replace("{framework_names}", str(data.technical_skills.frameworks))
            content = content.replace("{dev_tools_names}", str(data.technical_skills.dev_tools))
            content = content.replace("{library_names}", str(data.technical_skills.libraries))
            
        return content
        
    def render_to_pdf(self, data: LatexTemplateData, output_dir: str | Path, filename: str) -> Generator[str, None, Path]:
        """Render template to PDF with progress updates."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tex file
        tex_path = output_dir / f"{filename}.tex"
        filled_template = self.render(data)
        
        yield "Generated LaTeX content...\n"
        
        with open(tex_path, 'w') as f:
            f.write(filled_template)
            
        yield "Saved LaTeX file...\n"
            
        # Compile to PDF
        try:
            yield "Compiling PDF...\n"
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path.name],
                cwd=output_dir,
                capture_output=True,
                text=True,
                check=True
            )
            yield "LaTeX compilation output:\n"
            yield result.stdout + "\n"
            
            pdf_path = output_dir / f"{filename}.pdf"
            if not pdf_path.exists():
                yield "LaTeX error output:\n"
                yield result.stderr + "\n"
                raise RuntimeError("PDF compilation failed")
                
            yield "PDF generated successfully!\n"
            return pdf_path
            
        except subprocess.CalledProcessError as e:
            yield "LaTeX error output:\n"
            yield e.stdout + "\n"
            yield e.stderr + "\n"
            raise 