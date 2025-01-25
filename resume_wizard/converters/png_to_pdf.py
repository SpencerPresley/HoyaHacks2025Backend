from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import os

def get_resumes_dir():
    return Path(__file__).parent.parent / "resumes"

def get_image_paths():
    resumes_dir = get_resumes_dir()
    if not resumes_dir.exists():
        os.makedirs(resumes_dir)
    return list(resumes_dir.glob("*.png"))

def png_to_pdf():
    output_path_prefix = get_resumes_dir()
    image_paths = get_image_paths()
    
    if not image_paths:
        print("No PNG files found in the resumes directory")
        return
    
    for image_path in image_paths:
        try:
            # Create a canvas object with the specified page size
            output_pdf_path = output_path_prefix / (image_path.stem + ".pdf")
            c = canvas.Canvas(str(output_pdf_path), pagesize=letter)
            
            # Get the width and height of the page
            page_width, page_height = letter
            
            # Calculate scaling to maintain aspect ratio
            # Note: You might need PIL here for getting image dimensions
            # For now, we'll use a reasonable default scaling
            margin = 50  # 50 points margin
            usable_width = page_width - (2 * margin)
            usable_height = page_height - (2 * margin)
            
            # Draw the image centered on the page with margins
            c.drawImage(str(image_path), 
                       x=margin,
                       y=margin,
                       width=usable_width,
                       height=usable_height,
                       preserveAspectRatio=True)
            
            # Save the PDF
            c.save()
            print(f"Successfully converted {image_path.name} to PDF")
            
        except Exception as e:
            print(f"Error converting {image_path.name}: {str(e)}")

if __name__ == "__main__":
    png_to_pdf()