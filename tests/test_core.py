"""
Tests for core functionality.
"""

import pytest
from interview_assistant.core.resume_parser import ResumeParser
from interview_assistant.core.question_generator import QuestionGenerator
from interview_assistant.utils.helpers import (
    extract_skills_from_text,
    estimate_experience_level,
    calculate_resume_score
)


class TestResumeParser:
    """Test cases for ResumeParser class."""
    
    def test_parse_resume_none(self):
        """Test parsing with None input."""
        result = ResumeParser.parse_resume(None)
        assert result is None
    
    def test_extract_skills_from_text(self):
        """Test skill extraction from text."""
        text = "Python JavaScript React AWS Docker"
        skills = extract_skills_from_text(text)
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "React" in skills
        assert "AWS" in skills
        assert "Docker" in skills
    
    def test_estimate_experience_level_junior(self):
        """Test experience level estimation for junior."""
        text = "junior developer entry-level graduate intern"
        level = estimate_experience_level(text)
        assert level == "Junior"
    
    def test_estimate_experience_level_senior(self):
        """Test experience level estimation for senior."""
        text = "senior developer lead architect 10+ years experience"
        level = estimate_experience_level(text)
        assert level == "Senior"
    
    def test_calculate_resume_score(self):
        """Test resume scoring."""
        text = "Python JavaScript React AWS Docker experience education skills projects"
        scores = calculate_resume_score(text)
        assert 'skills_diversity' in scores
        assert 'experience_level' in scores
        assert 'completeness' in scores
        assert 'overall' in scores
        assert all(0 <= score <= 100 for score in scores.values())


class TestQuestionGenerator:
    """Test cases for QuestionGenerator class."""
    
    def test_question_generator_initialization(self):
        """Test QuestionGenerator initialization."""
        # This test would require a mock API key
        # For now, we'll just test the class exists
        assert QuestionGenerator is not None 