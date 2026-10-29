"""
Resume Parser Module
Handles extraction of text from PDF and Word documents
"""

import logging
import re
from typing import Any, Optional

from docx import Document
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class ResumeParser:
    """Class to parse resume files and extract text content"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text by removing excessive whitespace and newlines"""
        if not text:
            return ""

        # Remove excessive newlines and replace with single spaces
        text = re.sub(r"\n+", " ", text)

        # Remove excessive spaces (more than 2 consecutive spaces)
        text = re.sub(r" {2,}", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Normalize bullet points and special characters
        text = re.sub(r"●\s*", "• ", text)
        text = re.sub(r"•\s*", "• ", text)

        # Clean up common formatting artifacts
        text = re.sub(r"\s+([•\-])", r" \1", text)
        text = re.sub(r"([•\-])\s+", r"\1 ", text)

        # Remove any remaining excessive whitespace
        text = re.sub(r" +", " ", text)

        return text

    @staticmethod
    def extract_text_from_pdf(pdf_file: Any) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "

            # Clean the extracted text
            cleaned_text = ResumeParser.clean_text(text)
            return cleaned_text
        except Exception as _:
            logger.exception("Error reading PDF file")
            return None

    @staticmethod
    def extract_text_from_docx(docx_file: Any) -> Optional[str]:
        """Extract text from Word document"""
        try:
            doc = Document(docx_file)
            text = ""

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + " "

            # Clean the extracted text
            cleaned_text = ResumeParser.clean_text(text)
            return cleaned_text
        except Exception as _:
            logger.exception("Error reading Word document")
            return None

    @staticmethod
    def parse_resume(uploaded_file: Any) -> Optional[str]:
        """Parse resume file based on its type"""
        if uploaded_file is None:
            return None

        file_type = uploaded_file.type

        if file_type == "application/pdf":
            return ResumeParser.extract_text_from_pdf(uploaded_file)
        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            return ResumeParser.extract_text_from_docx(uploaded_file)
        else:
            return None
