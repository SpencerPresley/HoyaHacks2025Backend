from pathlib import Path
from .resume_pdf_dir import RESUMES_DIR

def get_absolute_path_to_resume(file_name: str) -> Path:
    return RESUMES_DIR / file_name