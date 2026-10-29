"""
Tests for question filtering logic in main.py.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_streamlit():
    """Mock streamlit module for testing display_questions."""
    with patch("interview_assistant.main.st") as mock_st:
        mock_st.session_state = {}
        mock_st.markdown = MagicMock()
        mock_st.subheader = MagicMock()
        mock_st.warning = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        mock_st.button = MagicMock(return_value=False)
        mock_st.rerun = MagicMock()
        yield mock_st


@pytest.fixture
def sample_questions():
    """Sample questions for filtering tests."""
    return [
        {
            "category": "Technical Skills",
            "difficulty": "Easy",
            "question": "What is Python?",
        },
        {
            "category": "Technical Skills",
            "difficulty": "Medium",
            "question": "Explain decorators.",
        },
        {
            "category": "Experience & Projects",
            "difficulty": "Hard",
            "question": "Describe your AWS project.",
        },
        {
            "category": "Behavioral",
            "difficulty": "Easy",
            "question": "Tell me about a conflict.",
        },
        {
            "category": "Problem Solving",
            "difficulty": "Medium",
            "question": "Reverse a linked list.",
        },
    ]


class TestDisplayQuestionsFiltering:
    """Test cases for display_questions filtering."""

    def test_no_filters_shows_all(self, mock_streamlit, sample_questions):
        from interview_assistant.main import display_questions

        display_questions(sample_questions, [], [])

        # All 5 questions should be displayed (no filtering)
        # Count subheader calls for categories
        category_calls = [
            call
            for call in mock_streamlit.subheader.call_args_list
            if "📂" in str(call)
        ]
        assert len(category_calls) == 4  # 4 unique categories

    def test_difficulty_filter_easy_only(self, mock_streamlit, sample_questions):
        from interview_assistant.main import display_questions

        display_questions(sample_questions, ["Easy"], [])

        category_calls = [
            call
            for call in mock_streamlit.subheader.call_args_list
            if "📂" in str(call)
        ]
        categories = [str(c[0][0]) for c in category_calls]
        # Easy questions: Technical Skills, Behavioral
        assert any("Technical Skills" in c for c in categories)
        assert any("Behavioral" in c for c in categories)

    def test_category_filter_technical_only(self, mock_streamlit, sample_questions):
        from interview_assistant.main import display_questions

        display_questions(sample_questions, [], ["Technical Skills"])

        category_calls = [
            call
            for call in mock_streamlit.subheader.call_args_list
            if "📂" in str(call)
        ]
        categories = [str(c[0][0]) for c in category_calls]
        assert len(categories) == 1
        assert "Technical Skills" in categories[0]

    def test_both_filters(self, mock_streamlit, sample_questions):
        from interview_assistant.main import display_questions

        display_questions(sample_questions, ["Easy"], ["Technical Skills"])

        category_calls = [
            call
            for call in mock_streamlit.subheader.call_args_list
            if "📂" in str(call)
        ]
        categories = [str(c[0][0]) for c in category_calls]
        assert len(categories) == 1
        assert "Technical Skills" in categories[0]

    def test_no_matches_shows_warning(self, mock_streamlit, sample_questions):
        from interview_assistant.main import display_questions

        display_questions(sample_questions, ["Hard"], ["Coding Test"])

        mock_streamlit.warning.assert_called()
        warning_msg = str(mock_streamlit.warning.call_args)
        assert "No questions match" in warning_msg

    def test_empty_questions_shows_warning(self, mock_streamlit):
        from interview_assistant.main import display_questions

        display_questions([], [], [])

        mock_streamlit.warning.assert_called()
        warning_msg = str(mock_streamlit.warning.call_args)
        assert "No questions match" in warning_msg


class TestMainImports:
    """Test that main.py imports correctly."""

    def test_main_module_imports(self):
        from interview_assistant.main import main, generate_questions, display_questions

        assert callable(main)
        assert callable(generate_questions)
        assert callable(display_questions)
