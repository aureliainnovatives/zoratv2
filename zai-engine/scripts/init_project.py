import os
from pathlib import Path

def create_directories():
    """Create necessary directories for the project."""
    base_dir = Path(__file__).parent.parent
    directories = [
        "storage/uploads",
        "storage/processed",
        "tests/test-files",
        "app/api/v1/endpoints",
        "app/services",
        "app/models",
        "app/core",
        "app/utils"
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def create_test_pdf():
    """Create a simple test PDF for testing."""
    test_file_path = Path(__file__).parent.parent / "tests/test-files/test.pdf"
    if not test_file_path.exists():
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="This is a test PDF document", ln=1, align="C")
            pdf.cell(200, 10, txt="Created for testing document processing", ln=1, align="C")
            pdf.output(str(test_file_path))
            print(f"Created test PDF: {test_file_path}")
        except ImportError:
            print("Please install fpdf package to create test PDF: pip install fpdf")

if __name__ == "__main__":
    create_directories()
    create_test_pdf() 