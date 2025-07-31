"""
Utility functions for the Interview Assistant application
"""

import re
from typing import List, Dict, Optional
import streamlit as st


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract technical skills from resume text using regex patterns
    
    Args:
        text: Resume text content
        
    Returns:
        List[str]: List of extracted skills
    """
    # Common technical skills patterns
    skill_patterns = [
        r'\b(?:Python|Java|JavaScript|C\+\+|C#|Go|Rust|Swift|Kotlin|TypeScript)\b',
        r'\b(?:React|Angular|Vue\.js|Node\.js|Express|Django|Flask|Spring|Laravel)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab)\b',
        r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|Cassandra)\b',
        r'\b(?:Machine Learning|AI|Deep Learning|TensorFlow|PyTorch|Scikit-learn)\b',
        r'\b(?:HTML|CSS|Bootstrap|Sass|Less|Webpack|Babel|npm|yarn)\b',
        r'\b(?:Linux|Unix|Windows|macOS|Shell|Bash|PowerShell)\b',
        r'\b(?:Agile|Scrum|Kanban|JIRA|Confluence|Slack|Teams)\b'
    ]
    
    skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update(matches)
    
    return list(skills)


def estimate_experience_level(text: str) -> str:
    """
    Estimate candidate experience level based on resume content
    
    Args:
        text: Resume text content
        
    Returns:
        str: Experience level (Junior, Mid-level, Senior, Lead)
    """
    text_lower = text.lower()
    
    # Keywords that indicate seniority
    senior_keywords = [
        'senior', 'lead', 'principal', 'architect', 'manager', 'director',
        '10+ years', '15+ years', '20+ years', 'extensive experience',
        'team lead', 'technical lead', 'mentor', 'coach'
    ]
    
    mid_keywords = [
        'mid-level', 'intermediate', '3+ years', '5+ years', '7+ years',
        'experienced', 'proficient', 'skilled'
    ]
    
    junior_keywords = [
        'junior', 'entry-level', 'graduate', 'intern', '0-2 years',
        'recent graduate', 'new graduate', 'student'
    ]
    
    # Count keyword occurrences
    senior_count = sum(1 for keyword in senior_keywords if keyword in text_lower)
    mid_count = sum(1 for keyword in mid_keywords if keyword in text_lower)
    junior_count = sum(1 for keyword in junior_keywords if keyword in text_lower)
    
    # Determine level based on keyword density
    if senior_count > mid_count and senior_count > junior_count:
        return "Senior"
    elif mid_count > junior_count:
        return "Mid-level"
    else:
        return "Junior"


def extract_education_info(text: str) -> Dict[str, str]:
    """
    Extract education information from resume text
    
    Args:
        text: Resume text content
        
    Returns:
        Dict[str, str]: Education information
    """
    education_info = {}
    
    # Degree patterns
    degree_patterns = [
        r'\b(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|M\.?A\.?|B\.?A\.?|B\.?E\.?|M\.?E\.?)\b',
        r'\b(?:Computer Science|Software Engineering|Information Technology|Data Science)\b'
    ]
    
    # University patterns
    university_patterns = [
        r'\b(?:University|College|Institute|School)\s+of\s+\w+',
        r'\b\w+\s+(?:University|College|Institute)\b'
    ]
    
    # Extract degree
    for pattern in degree_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            education_info['degree'] = match.group()
            break
    
    # Extract university
    for pattern in university_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            education_info['university'] = match.group()
            break
    
    return education_info


def calculate_resume_score(text: str) -> Dict[str, float]:
    """
    Calculate various scores for the resume
    
    Args:
        text: Resume text content
        
    Returns:
        Dict[str, float]: Various scores (0-100)
    """
    scores = {}
    
    # Skills diversity score
    skills = extract_skills_from_text(text)
    skills_score = min(len(skills) * 5, 100)  # 5 points per skill, max 100
    scores['skills_diversity'] = skills_score
    
    # Experience level score
    experience_level = estimate_experience_level(text)
    experience_scores = {
        'Junior': 30,
        'Mid-level': 60,
        'Senior': 90
    }
    scores['experience_level'] = experience_scores.get(experience_level, 50)
    
    # Content completeness score
    sections = ['experience', 'education', 'skills', 'projects']
    section_count = sum(1 for section in sections if section.lower() in text.lower())
    completeness_score = (section_count / len(sections)) * 100
    scores['completeness'] = completeness_score
    
    # Overall score
    scores['overall'] = (scores['skills_diversity'] + scores['experience_level'] + scores['completeness']) / 3
    
    return scores


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


def create_sample_resume() -> str:
    """
    Create a sample resume for testing purposes
    
    Returns:
        str: Sample resume text
    """
    return """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    SUMMARY
    Experienced software engineer with 5+ years of expertise in full-stack development, 
    specializing in Python, JavaScript, and cloud technologies. Proven track record of 
    delivering scalable web applications and leading development teams.
    
    TECHNICAL SKILLS
    Programming Languages: Python, JavaScript, TypeScript, Java, SQL
    Frameworks & Libraries: React, Node.js, Django, Flask, Express.js
    Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Git
    Databases: PostgreSQL, MongoDB, Redis, MySQL
    Tools & Platforms: Linux, VS Code, JIRA, Agile/Scrum
    
    EXPERIENCE
    
    Senior Software Engineer | TechCorp Inc. | 2021 - Present
    • Led development of microservices architecture serving 1M+ users
    • Mentored 3 junior developers and conducted code reviews
    • Implemented CI/CD pipelines reducing deployment time by 60%
    • Technologies: Python, React, AWS, Docker, PostgreSQL
    
    Software Engineer | StartupXYZ | 2019 - 2021
    • Developed RESTful APIs and frontend components for SaaS platform
    • Collaborated with cross-functional teams using Agile methodology
    • Optimized database queries improving performance by 40%
    • Technologies: JavaScript, Node.js, MongoDB, Express.js
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2015 - 2019
    
    PROJECTS
    E-commerce Platform: Full-stack web application with payment integration
    Machine Learning Dashboard: Real-time data visualization using Python and React
    Task Management App: Mobile-responsive web app with real-time updates
    """ 