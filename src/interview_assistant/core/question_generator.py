"""
Question Generator Module
Uses OpenAI API to generate interview questions based on resume content
"""

import openai
import streamlit as st
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuestionGenerator:
    """Class to generate interview questions using OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI client with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
            st.stop()
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-1106-preview")
    
    def generate_questions(self, resume_text: str, question_count: int = 10) -> List[Dict]:
        """
        Generate interview questions based on resume content
        
        Args:
            resume_text: Extracted text from resume
            question_count: Number of questions to generate
            
        Returns:
            List[Dict]: List of questions with categories and details
        """
        try:
            # Create the prompt for question generation
            prompt = self._create_question_prompt(resume_text, question_count)
            
            # Generate questions using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer who creates relevant, insightful interview questions based on candidate resumes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            questions_text = response.choices[0].message.content
            return self._parse_questions(questions_text)
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return []
    
    def _create_question_prompt(self, resume_text: str, question_count: int) -> str:
        """
        Create a detailed prompt for question generation
        
        Args:
            resume_text: Resume content
            question_count: Number of questions to generate
            
        Returns:
            str: Formatted prompt for OpenAI
        """
        return f"""
        Based on the following resume, generate {question_count} relevant interview questions for a technical role.
        
        Resume Content:
        {resume_text[:3000]}  # Limit to first 3000 characters to manage token usage
        
        Please generate questions in the following format:
        
        TECHNICAL SKILLS:
        1. [Question about specific technical skills mentioned]
        2. [Question about technical experience]
        
        EXPERIENCE & PROJECTS:
        1. [Question about specific projects or work experience]
        2. [Question about achievements and responsibilities]
        
        PROBLEM SOLVING:
        1. [Scenario-based question related to their background]
        2. [Question about how they approach technical challenges]
        
        BEHAVIORAL:
        1. [Question about teamwork, leadership, or communication]
        2. [Question about handling difficult situations]
        
        Please ensure questions are:
        - Specific to the candidate's background and experience
        - Appropriate for their skill level
        - Mix of easy, medium, and challenging questions
        - Relevant to technical roles
        - Professional and respectful
        
        Format each question clearly and provide context when needed.
        """
    
    def _parse_questions(self, questions_text: str) -> List[Dict]:
        """
        Parse the generated questions text into structured format
        
        Args:
            questions_text: Raw text from OpenAI response
            
        Returns:
            List[Dict]: Structured questions with categories
        """
        questions = []
        current_category = "General"
        
        lines = questions_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a category header
            if line.endswith(':') and any(category in line.upper() for category in ['TECHNICAL', 'EXPERIENCE', 'PROBLEM', 'BEHAVIORAL']):
                current_category = line[:-1]  # Remove the colon
                continue
            
            # Check if line starts with a number (question)
            if line and line[0].isdigit() and '. ' in line:
                question_text = line.split('. ', 1)[1] if '. ' in line else line
                questions.append({
                    'category': current_category,
                    'question': question_text,
                    'difficulty': self._estimate_difficulty(question_text, current_category)
                })
        
        return questions
    
    def _estimate_difficulty(self, question: str, category: str) -> str:
        """
        Estimate question difficulty based on content and category
        
        Args:
            question: Question text
            category: Question category
            
        Returns:
            str: Difficulty level (Easy, Medium, Hard)
        """
        # Simple heuristic for difficulty estimation
        question_lower = question.lower()
        
        # Easy indicators
        easy_keywords = ['what is', 'define', 'explain', 'describe', 'basic', 'fundamental']
        if any(keyword in question_lower for keyword in easy_keywords):
            return "Easy"
        
        # Hard indicators
        hard_keywords = ['design', 'architecture', 'optimize', 'scale', 'complex', 'advanced', 'implement']
        if any(keyword in question_lower for keyword in hard_keywords):
            return "Hard"
        
        # Medium by default
        return "Medium" 