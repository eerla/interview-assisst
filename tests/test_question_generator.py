"""
Tests for QuestionGenerator core functionality with mocked OpenAI client.
"""

import json
from unittest.mock import MagicMock, patch

import openai
import pytest

from interview_assistant.core.question_generator import QuestionGenerator


class TestQuestionGeneratorInit:
    """Test cases for QuestionGenerator initialization."""

    def test_init_with_api_key(self, mocker):
        mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test12345"})
        with patch(
            "interview_assistant.core.question_generator.openai.OpenAI"
        ) as mock_client:
            gen = QuestionGenerator()
            mock_client.assert_called_once_with(api_key="sk-test12345")
            assert gen.model == "gpt-4-1106-preview"

    def test_init_with_custom_model(self, mocker):
        mocker.patch.dict(
            "os.environ", {"OPENAI_API_KEY": "sk-test12345", "OPENAI_MODEL": "gpt-4"}
        )
        with patch("interview_assistant.core.question_generator.openai.OpenAI"):
            gen = QuestionGenerator()
            assert gen.model == "gpt-4"

    def test_init_without_api_key_raises(self, mocker):
        mocker.patch.dict("os.environ", {}, clear=True)
        with pytest.raises(ValueError, match="OpenAI API key not found"):
            QuestionGenerator()


class TestQuestionGeneratorSanitize:
    """Test cases for _sanitize_resume_text."""

    def test_sanitize_none(self, generator):
        result = generator._sanitize_resume_text(None)
        assert result == ""

    def test_sanitize_empty(self, generator):
        result = generator._sanitize_resume_text("")
        assert result == ""

    def test_sanitize_removes_null_bytes(self, generator):
        result = generator._sanitize_resume_text("hello\x00world")
        assert "\x00" not in result
        assert result == "helloworld"

    def test_sanitize_truncates_long_text(self, generator):
        long_text = "x" * 60000
        result = generator._sanitize_resume_text(long_text)
        assert len(result) <= 50000

    def test_sanitize_strips_control_chars(self, generator):
        result = generator._sanitize_resume_text("hello\x01world\x7f")
        assert "\x01" not in result
        assert "\x7f" not in result


class TestQuestionGeneratorValidateResponse:
    """Test cases for _validate_response_shape."""

    def test_validate_valid_shape(self, generator):
        data = {
            "questions": [
                {
                    "category": "Technical Skills",
                    "difficulty": "Easy",
                    "question": "What is Python?",
                }
            ],
            "insights": {"technologies": ["Python"]},
            "ats_suggestions": ["Add keywords"],
        }
        result = generator._validate_response_shape(data)
        assert len(result["questions"]) == 1
        assert result["questions"][0]["question"] == "What is Python?"
        assert result["insights"]["technologies"] == ["Python"]
        assert result["ats_suggestions"] == ["Add keywords"]

    def test_validate_not_dict(self, generator):
        result = generator._validate_response_shape(["not", "a", "dict"])
        assert result["questions"] == []
        assert result["insights"] == {}
        assert result["ats_suggestions"] == []

    def test_validate_questions_not_list(self, generator):
        data = {"questions": "not a list"}
        result = generator._validate_response_shape(data)
        assert result["questions"] == []

    def test_validate_drops_incomplete_questions(self, generator):
        data = {
            "questions": [
                {
                    "category": "Technical Skills",
                    "difficulty": "Easy",
                },  # missing question
                {"question": "Only question"},  # missing category/difficulty
                {
                    "category": "Technical Skills",
                    "difficulty": "Easy",
                    "question": "Valid one",
                },
            ]
        }
        result = generator._validate_response_shape(data)
        assert len(result["questions"]) == 1
        assert result["questions"][0]["question"] == "Valid one"


class TestQuestionGeneratorGenerateQuestions:
    """Test cases for generate_questions."""

    def test_generate_questions_valid_json(self, generator, mocker):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "questions": [
                    {
                        "category": "Technical Skills",
                        "difficulty": "Easy",
                        "question": "What is Python?",
                    }
                ],
                "insights": {"technologies": ["Python"]},
                "ats_suggestions": ["Add keywords"],
            }
        )
        generator.client.chat.completions.create = MagicMock(return_value=mock_response)

        result = generator.generate_questions(
            "resume text", 5, ["Easy"], ["Technical Skills"]
        )

        assert len(result["questions"]) == 1
        assert result["questions"][0]["question"] == "What is Python?"
        assert result["insights"]["technologies"] == ["Python"]
        assert result["ats_suggestions"] == ["Add keywords"]

    def test_generate_questions_invalid_json(self, generator, mocker):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "not valid json {{{"
        generator.client.chat.completions.create = MagicMock(return_value=mock_response)

        result = generator.generate_questions(
            "resume text", 5, ["Easy"], ["Technical Skills"]
        )

        assert result["questions"] == []
        assert result["insights"] == {}
        assert result["ats_suggestions"] == []

    def test_generate_questions_empty_response(self, generator, mocker):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = ""
        generator.client.chat.completions.create = MagicMock(return_value=mock_response)

        result = generator.generate_questions(
            "resume text", 5, ["Easy"], ["Technical Skills"]
        )

        assert result["questions"] == []
        assert result["insights"] == {}
        assert result["ats_suggestions"] == []

    def test_generate_questions_api_error(self, generator, mocker):
        generator.client.chat.completions.create = MagicMock(
            side_effect=Exception("API error")
        )

        with pytest.raises(RuntimeError, match="Failed to generate questions"):
            generator.generate_questions(
                "resume text", 5, ["Easy"], ["Technical Skills"]
            )

    def test_generate_questions_count_capped_at_10(self, generator, mocker):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "questions": [],
                "insights": {},
                "ats_suggestions": [],
            }
        )
        mock_create = MagicMock(return_value=mock_response)
        generator.client.chat.completions.create = mock_create

        generator.generate_questions("resume text", 15, ["Easy"], ["Technical Skills"])

        # Verify the call was made with question_count capped at 10
        call_args = mock_create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        assert "Generate 10 interview questions" in prompt

    def test_generate_questions_defaults_none_filters(self, generator, mocker):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "questions": [],
                "insights": {},
                "ats_suggestions": [],
            }
        )
        mock_create = MagicMock(return_value=mock_response)
        generator.client.chat.completions.create = mock_create

        generator.generate_questions("resume text", 5)

        call_args = mock_create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        assert "Difficulty levels: Easy" in prompt
        assert "Questions for categories: Technical Skills" in prompt


class TestQuestionGeneratorRetry:
    """Test cases for retry behavior on transient OpenAI errors."""

    def test_retry_on_rate_limit(self, generator, mocker):
        """Verify that RateLimitError triggers retry."""
        mock_create = MagicMock()
        mock_create.side_effect = [
            openai.RateLimitError("Rate limited", response=MagicMock(), body=None),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content=json.dumps(
                                {"questions": [], "insights": {}, "ats_suggestions": []}
                            )
                        )
                    )
                ]
            ),
        ]
        generator.client.chat.completions.create = mock_create

        result = generator.generate_questions(
            "resume text", 5, ["Easy"], ["Technical Skills"]
        )

        assert mock_create.call_count == 2
        assert result["questions"] == []
