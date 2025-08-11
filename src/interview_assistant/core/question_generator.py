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
                                category_filter: list = ["Technical Skills"]) -> List[Dict]:
        """
        Generate interview questions based on resume content
        
        Args:
            resume_text: Extracted text from resume
            question_count: Number of questions to generate (max 10)
            difficulty_filter: List of difficulty levels to include
            category_filter: List of categories to include
            
        Returns:
            List[Dict]: List of questions with categories and difficulty levels
        """
        try:
            # Validate question count
            if question_count > 10:
                question_count = 10
                st.warning("Question count limited to maximum of 10")
            
            # Create the prompt for question generation
            prompt = self._create_question_prompt(resume_text, question_count, difficulty_filter, category_filter)
            

            # Generate questions using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who creates relevant and insightful interview questions based on candidate resumes. You are also expert in python, pyspark, java, c++, c, javascript, html, css, sql databases, nosql databases, data structures, data modeling, algorithms, system design, microservices, distributed systems, cloud computing, artificial intelligence, machine learning, deep learning, natural language processing, computer vision, robotics, and other related technologies. You are also expert in data analysis, data visualization, data engineering, data science, data warehousing, data modeling, data cleaning, data integration, data transformation, data loading, data unloading, data archiving, data backup, data recovery, data replication, data synchronization, data migration, REST APIs, CICD pipelines, and other related technologies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Parse the response
            questions_text = response.choices[0].message.content

            
            questions = self._parse_questions(questions_text)
            # Validate that we got the expected number of questions
            if len(questions) != question_count:
                st.warning(f"Generated {len(questions)} questions instead of requested {question_count}.\
                     This may be due to LLM response format.")
            
            return questions
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.error("Please check your OpenAI API key and try again.")
            return []
    
    def _create_question_prompt(self, resume_text: str, question_count: int, difficulty_filter: list, category_filter: list) -> str:
        """
        Create a detailed prompt for question generation
        
        Args:
            resume_text: Resume content
            question_count: Number of questions to generate
            difficulty_filter: List of difficulty levels
            category_filter: List of categories
            
        Returns:
            str: Formatted prompt for OpenAI
        """
        return f"""
        Based on the following resume, generate exactly {question_count} relevant interview questions for a technical role.
        
        REQUIREMENTS:
        - Difficulty levels: {', '.join(difficulty_filter)}
        - Categories: {', '.join(category_filter)}
        - Total questions: {question_count}
        
        Resume Content:
        {resume_text[:4000]}
        
        Generate questions in this EXACT format with category headers:
        
        {self._get_format_example(category_filter)}
        
        CRITICAL FORMATTING RULES: 
        - You MUST include the category headers exactly as shown above
        - Start each category with "CATEGORY_NAME:" (e.g., "TECHNICAL SKILLS:")
        - Then list numbered questions under each category
        - Each question must start with [DIFFICULTY] where difficulty is one of: {', '.join(difficulty_filter)}
        - Use only the specified categories: {', '.join(category_filter)}
        - Make questions specific to the candidate's background and experience
        - No additional text, explanations, or markdown formatting
        - Example format:
          TECHNICAL SKILLS:
          1. [EASY] What is your experience with Python?
          2. [MEDIUM] Can you explain the difference between a list and a tuple?
        """
    
    def _get_format_example(self, categories: list) -> str:
        """Get format example based on selected categories"""
        examples = []
        for category in categories:
            examples.append(f"{category.upper()}:\n1. [EASY] [Question text]\n2. [MEDIUM] [Question text]\n3. [HARD] [Question text]")
        return "\n\n".join(examples)
    
    def _parse_questions(self, questions_text: str) -> List[Dict]:
        """
        Parse the generated questions text into structured format
        
        Args:
            questions_text: Raw text from OpenAI response
            
        Returns:
            List[Dict]: Structured questions with categories and difficulty levels
        """
        questions = []
        current_category = None
        lines = questions_text.split('\n')
        print("--------------------------------")
        for line in lines:
            print(f"{line}")
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a category header (more flexible detection)
            if line.endswith(':') and len(line) > 1:
                # Remove the colon and clean up
                current_category = line[:-1].strip()
                # Convert to title case for consistency
                current_category = current_category.title()

                continue
            
            # Check if line starts with a number (question)
            if line and line[0].isdigit() and '. ' in line:
                question_text = line.split('. ', 1)[1] if '. ' in line else line
                
                # Extract difficulty and clean question text
                difficulty, clean_question = self._extract_difficulty_and_clean(question_text)
                
                if current_category and difficulty and clean_question:
                    questions.append({
                        'category': current_category,
                        'question': clean_question,
                        'difficulty': difficulty
                    })

        return questions
    
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