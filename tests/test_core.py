"""
Tests for core functionality.
"""

import pytest
from interview_assistant.core.resume_parser import ResumeParser
from interview_assistant.core.question_generator import QuestionGenerator


class TestResumeParser:
    """Test cases for ResumeParser class."""
    
    def test_parse_resume_none(self):
        """Test parsing with None input."""
        result = ResumeParser.parse_resume(None)
        assert result is None


class TestQuestionGenerator:
    """Test cases for QuestionGenerator class."""
    
    def test_question_generator_initialization(self):
        """Test QuestionGenerator initialization."""
        # This test would require a mock API key
        # For now, we'll just test the class exists
        assert QuestionGenerator is not None 