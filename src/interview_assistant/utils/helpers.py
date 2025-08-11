"""
Utility functions for the Interview Assistant application
"""

import streamlit as st
from typing import List, Dict


def format_questions_for_export(questions: List[Dict]) -> str:
    """
    Format questions for export in a clean text format
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        str: Formatted text
    """
    if not questions:
        return "No questions available for export."
    
    # Group by category
    categories = {}
    for question in questions:
        category = question['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(question)
    
    # Format output
    output = "INTERVIEW QUESTIONS\n"
    output += "=" * 50 + "\n\n"
    
    for category, category_questions in categories.items():
        output += f"{category.upper()}\n"
        output += "-" * len(category) + "\n"
        
        for i, question in enumerate(category_questions, 1):
            output += f"{i}. {question['question']}\n"
            output += f"   Difficulty: {question['difficulty']}\n\n"
        
        output += "\n"
    
    return output


def validate_file_upload(uploaded_file) -> bool:
    """
    Validate uploaded file format and size
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        bool: True if valid, False otherwise
    """
    if uploaded_file is None:
        return False
    
    # Check file type
    allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if uploaded_file.type not in allowed_types:
        st.error("❌ Invalid file type. Please upload a PDF or Word document.")
        return False
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if uploaded_file.size > max_size:
        st.error("❌ File too large. Please upload a file smaller than 10MB.")
        return False
    
    return True 