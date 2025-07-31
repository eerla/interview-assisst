"""
Resume Parser Module
Handles extraction of text from PDF and Word documents
"""

import PyPDF2
from docx import Document
import streamlit as st
from typing import Optional


class ResumeParser:
    """Class to parse resume files and extract text content"""
    
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
                text += page.extract_text() + "\n"
                
            return text.strip()
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
                text += paragraph.text + "\n"
                
            return text.strip()
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