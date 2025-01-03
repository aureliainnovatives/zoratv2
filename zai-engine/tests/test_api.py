import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os

from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_pdf():
    # Create a simple PDF for testing
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF Document", ln=1, align="C")
    pdf.cell(200, 10, txt="This is a test document for ZAI Engine", ln=1, align="L")
    
    # Save to test directory
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    pdf_path = test_dir / "test.pdf"
    pdf.output(str(pdf_path))
    yield pdf_path
    # Cleanup
    os.remove(pdf_path)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_upload_document(sample_pdf):
    with open(sample_pdf, "rb") as f:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "processing"
    assert "file_path" in data

def test_list_documents():
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    documents = response.json()
    assert isinstance(documents, list)
    if documents:
        assert "filename" in documents[0]
        assert "status" in documents[0]

def test_get_document_not_found():
    response = client.get("/api/v1/documents/nonexistent_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found" 