"""
Question Generator Module
Uses OpenAI API to generate interview questions based on resume content
"""

import openai
import streamlit as st
from typing import List, Dict
import os

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
    
    def generate_questions(self, resume_text: str, 
                                question_count: int = 10, 
                                difficulty_filter: list = ["Easy"], 
                                category_filter: list = ["Technical Skills"]) -> Dict:
        """
        Generate interview questions, insights, and ATS suggestions based on resume content
        
        Args:
            resume_text: Extracted text from resume
            question_count: Number of questions to generate (max 10)
            difficulty_filter: List of difficulty levels to include
            category_filter: List of categories to include
            
        Returns:
            Dict: Complete response with questions, insights, and ATS suggestions
        """
        try:
            # Validate question count
            if question_count > 10:
                question_count = 10
                st.warning("Question count limited to maximum of 10")
            
            # Handle coding test instructions
            coding_test_instruction = ""
            if "Coding Test" in category_filter:
                coding_test_instruction = (
                    "\n\nAdditionally, generate up to 2 LeetCode-style coding questions in Python for the 'Coding Test' category. "
                    "Each coding question should include: a clear problem statement, input/output format, at least 2 sample test cases, and difficulty based on the selected level. "
                    "Format the coding questions with a markdown code block for the function signature and test cases."
                )
            
            # Create the prompt for question generation
            prompt = self._create_question_prompt(resume_text, question_count, difficulty_filter, category_filter) + coding_test_instruction
            
            # Generate questions using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who creates relevant and insightful interview questions based on candidate resumes. You are also expert in python, pyspark, java, c++, c, javascript, html, css, sql databases, nosql databases, data structures, data modeling, algorithms, system design, microservices, distributed systems, cloud computing, artificial intelligence, machine learning, deep learning, natural language processing, computer vision, robotics, and other related technologies. You are also expert in data analysis, data visualization, data engineering, data science, data warehousing, data modeling, data cleaning, data integration, data transformation, data loading, data unloading, data archiving, data backup, data recovery, data replication, data synchronization, data migration, REST APIs, CICD pipelines, and other related technologies."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4000
            )
            
            # Parse the complete response
            llm_response = response.choices[0].message.content
            st.write("Debug: Raw LLM response received")
            st.write(f"Debug: Response length: {len(llm_response)} characters")
            
            if not llm_response or llm_response.strip() == "":
                st.error("Empty response from OpenAI. This might be due to API issues or content filtering.")
                return {
                    "questions": [],
                    "insights": {},
                    "ats_suggestions": []
                }
            
            # Parse and return the complete structured response
            import json
            try:
                data = json.loads(llm_response)
                st.write("Debug: JSON parsed successfully")
                
                result = {
                    "questions": data.get("questions", []),
                    "insights": data.get("insights", {}),
                    "ats_suggestions": data.get("ats_suggestions", [])
                }
                
                st.write(f"Debug: Returning {len(result['questions'])} questions")
                return result
                
            except json.JSONDecodeError as e:
                st.error(f"JSON parsing error: {e}")
                st.write("Debug: Raw response was:")
                st.code(llm_response[:500])  # Show first 500 chars
                return {
                    "questions": [],
                    "insights": {},
                    "ats_suggestions": []
                }
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.error("Please check your OpenAI API key and try again.")
            return {
                "questions": [],
                "insights": {},
                "ats_suggestions": []
            }
    
    def _create_question_prompt(self, resume_text: str, question_count: int, difficulty_filter: list, category_filter: list) -> str:
            """
            Create a detailed prompt for question generation, key insights extraction, and ATS suggestions
    
            Args:
                    resume_text: Resume content
                    question_count: Number of questions to generate
                    difficulty_filter: List of difficulty levels
                    category_filter: List of categories
        
            Returns:
                    str: Formatted prompt for OpenAI
            """
            return f"""Analyze this resume and generate interview questions.

RESUME:
{resume_text[:3000]}

TASKS:
1. Generate {question_count} interview questions
2. Extract key insights 
3. Provide ATS suggestions

REQUIREMENTS:
- Questions for categories: {', '.join(category_filter)}
- Difficulty levels: {', '.join(difficulty_filter)}
- Each question needs: category, difficulty, question text

RESPONSE FORMAT (JSON only):
{{
    "questions": [
        {{"category": "Technical Skills", "difficulty": "Easy", "question": "What experience do you have with Python?"}},
        {{"category": "Technical Skills", "difficulty": "Medium", "question": "Describe a complex algorithm you implemented."}}
    ],
    "insights": {{
        "technologies": ["Python", "React", "AWS"],
        "companies": [{{"name": "Tech Corp", "duration": "2 years"}}],
        "total_years_experience": 5,
        "education": [{{"degree": "BS Computer Science", "institution": "University"}}],
        "certifications": ["AWS Certified"],
        "major_projects": ["E-commerce platform"]
    }},
    "ats_suggestions": ["Add more keywords", "Quantify achievements"]
}}

Return ONLY valid JSON. No explanations."""

    def _get_format_example(self, categories: list) -> str:
        """Get format example based on selected categories"""
        examples = []
        for category in categories:
            examples.append(f"{category.upper()}:\n1. [Easy] [Question text]\n2. [Medium] [Question text]\n3. [Hard] [Question text]")
        return "\n\n".join(examples)
    
    def _parse_questions(self, llm_response: str) -> List[Dict]:
        """
        Parse the questions from the LLM's JSON response.
        Args:
            llm_response: Raw text from OpenAI response (expected to be JSON)
        Returns:
            List[Dict]: Structured questions with categories and difficulty levels
        """
        import json
        try:
            data = json.loads(llm_response)
            questions = data.get("questions", [])
            return questions
        except Exception as e:
            st.error(f"Failed to parse questions from LLM response: {e}")
            return []

    def _parse_insights(self, llm_response: str) -> Dict:
        """
        Parse the key insights from the LLM's JSON response.
        Args:
            llm_response: Raw text from OpenAI response (expected to be JSON)
        Returns:
            Dict: Extracted insights
        """
        import json
        try:
            data = json.loads(llm_response)
            insights = data.get("insights", {})
            return insights
        except Exception as e:
            st.error(f"Failed to parse insights from LLM response: {e}")
            return {}

    def _parse_ats_suggestions(self, llm_response: str) -> List[str]:
        """
        Parse the ATS suggestions from the LLM's JSON response.
        Args:
            llm_response: Raw text from OpenAI response (expected to be JSON)
        Returns:
            List[str]: List of ATS suggestions
        """
        import json
        try:
            data = json.loads(llm_response)
            ats_suggestions = data.get("ats_suggestions", [])
            return ats_suggestions
        except Exception as e:
            st.error(f"Failed to parse ATS suggestions from LLM response: {e}")
            return []
    
    def _extract_difficulty_and_clean(self, question_text: str) -> tuple:
        """
        Extract difficulty level and clean question text
        
        Args:
            question_text: Question text that may contain difficulty markers
            
        Returns:
            tuple: (difficulty, clean_question) or (None, None) if invalid
        """
        # Check for explicit difficulty markers (case insensitive)
        question_upper = question_text.upper()
        
        if '[EASY]' in question_upper:
            difficulty = "Easy"
            clean_question = question_text.replace('[EASY]', '').replace('[easy]', '').strip()
        elif '[HARD]' in question_upper:
            difficulty = "Hard"
            clean_question = question_text.replace('[HARD]', '').replace('[hard]', '').strip()
        elif '[MEDIUM]' in question_upper:
            difficulty = "Medium"
            clean_question = question_text.replace('[MEDIUM]', '').replace('[medium]', '').strip()
        else:
            # Try to find difficulty in the text without brackets
            if 'EASY' in question_upper and question_upper.find('EASY') < 20:  # Within first 20 chars
                difficulty = "Easy"
                clean_question = question_text.replace('EASY', '').replace('easy', '').strip()
            elif 'HARD' in question_upper and question_upper.find('HARD') < 20:
                difficulty = "Hard"
                clean_question = question_text.replace('HARD', '').replace('hard', '').strip()
            elif 'MEDIUM' in question_upper and question_upper.find('MEDIUM') < 20:
                difficulty = "Medium"
                clean_question = question_text.replace('MEDIUM', '').replace('medium', '').strip()
            else:
                return None, None
        
        # Clean up extra brackets, whitespace, and normalize
        clean_question = clean_question.replace('[', '').replace(']', '').strip()
        clean_question = ' '.join(clean_question.split())  # Normalize multiple spaces
        
        return difficulty, clean_question 

if __name__ == "__main__":
    pass