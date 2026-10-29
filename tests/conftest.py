"""
Pytest configuration and fixtures for Interview Assistant tests.
"""

import io
import pytest

from interview_assistant.core.resume_parser import ResumeParser
from interview_assistant.core.question_generator import QuestionGenerator


@pytest.fixture
def sample_pdf_bytes():
    """Generate a minimal valid PDF file as bytes."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # Add some text via a simple approach - pypdf text injection is limited,
    # so we create a PDF with a page and rely on extraction returning empty/whitespace.
    # For a text-bearing PDF we'd need reportlab; here we test the parsing path.
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture
def sample_docx_bytes():
    """Generate a minimal valid DOCX file as bytes."""
    from docx import Document

    doc = Document()
    doc.add_paragraph("John Doe")
    doc.add_paragraph("Software Engineer at Tech Corp (2018-2023)")
    doc.add_paragraph("Skills: Python, AWS, React")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def sample_resume_text():
    """Sample resume text for parsing tests."""
    return """
    John Doe
    Software Engineer

    Experience:
    - Tech Corp, Senior Software Engineer (2018-2023)
    - Startup Inc, Software Engineer (2015-2018)

    Skills: Python, AWS, React, SQL, Docker

    Education:
    - BS Computer Science, University of Technology (2015)

    Certifications: AWS Certified Solutions Architect

    Projects:
    - E-commerce platform built with React and AWS
    """


@pytest.fixture
def parser():
    """ResumeParser instance."""
    return ResumeParser()


@pytest.fixture
def generator(mocker):
    """QuestionGenerator instance with mocked OpenAI client."""
    # Prevent __init__ from requiring env var by patching os.getenv
    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test-key-12345"})
    gen = QuestionGenerator()
    return gen
