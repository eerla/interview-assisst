"""
Resume Parser Module
Handles extraction of text from PDF and Word documents
"""

import PyPDF2
from docx import Document
import streamlit as st
from typing import Optional
import re


class ResumeParser:
    """Class to parse resume files and extract text content"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text by removing excessive whitespace and newlines
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove excessive newlines and replace with single spaces
        text = re.sub(r'\n+', ' ', text)
        
        # Remove excessive spaces (more than 2 consecutive spaces)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize bullet points and special characters
        text = re.sub(r'●\s*', '• ', text)
        text = re.sub(r'•\s*', '• ', text)
        
        # Clean up common formatting artifacts
        text = re.sub(r'\s+([•\-])', r' \1', text)  # Ensure proper spacing before bullets
        text = re.sub(r'([•\-])\s+', r'\1 ', text)  # Ensure proper spacing after bullets
        
        # Remove any remaining excessive whitespace
        text = re.sub(r' +', ' ', text)
        
        return text
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            pdf_file: Uploaded PDF file object
            
        Returns:
            str: Extracted text from PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
                
            # Clean the extracted text
            cleaned_text = ResumeParser.clean_text(text)
            return cleaned_text
        except Exception as e:
            st.error(f"Error reading PDF file: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_docx(docx_file) -> Optional[str]:
        """
        Extract text from Word document
        
        Args:
            docx_file: Uploaded Word file object
            
        Returns:
            str: Extracted text from Word document
        """
        try:
            doc = Document(docx_file)
            text = ""
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Only add non-empty paragraphs
                    text += paragraph.text + " "
                
            # Clean the extracted text
            cleaned_text = ResumeParser.clean_text(text)
            return cleaned_text
        except Exception as e:
            st.error(f"Error reading Word document: {str(e)}")
            return None
    
    @staticmethod
    def parse_resume(uploaded_file) -> Optional[str]:
        """
        Parse resume file based on its type
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from resume
        """
        if uploaded_file is None:
            return None
            
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            return ResumeParser.extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return ResumeParser.extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a PDF or Word document.")
            return None 