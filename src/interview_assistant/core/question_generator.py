"""
Question Generator Module
Uses OpenAI API to generate interview questions based on resume content
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)

MAX_RESUME_CHARS = 50_000
VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}
VALID_CATEGORIES = {
    "Technical Skills",
    "Experience & Projects",
    "Problem Solving",
    "Behavioral",
    "Coding Test",
}

# Case-insensitive lookup maps for normalizing LLM output
_DIFFICULTY_LOOKUP = {d.lower(): d for d in VALID_DIFFICULTIES}
_CATEGORY_LOOKUP = {c.lower(): c for c in VALID_CATEGORIES}


def _normalize_difficulty(value: str) -> Optional[str]:
    """Normalize difficulty string to canonical form."""
    return _DIFFICULTY_LOOKUP.get(value.strip().lower())


def _normalize_category(value: str) -> Optional[str]:
    """Normalize category string to canonical form."""
    return _CATEGORY_LOOKUP.get(value.strip().lower())


MARKDOWN_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class QuestionGenerator:
    """Class to generate interview questions using OpenAI API"""

    def __init__(self) -> None:
        """Initialize OpenAI client with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables."
            )

        self.client = openai.OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-1106-preview")

    def _sanitize_resume_text(self, resume_text: str) -> str:
        """Sanitize resume text before sending to the model."""
        if not resume_text:
            return ""
        text = resume_text.replace("\x00", "")
        text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", text)
        if len(text) > MAX_RESUME_CHARS:
            logger.warning(
                f"Resume text truncated from {len(text)} to {MAX_RESUME_CHARS} characters"
            )
            text = text[:MAX_RESUME_CHARS]
        return text.strip()

    def _validate_response_shape(self, data: Any) -> Dict:
        """Validate that the parsed JSON matches the expected shape."""
        if not isinstance(data, dict):
            return {
                "questions": [],
                "insights": {},
                "ats_suggestions": [],
            }

        questions = data.get("questions", [])
        if not isinstance(questions, list):
            questions = []

        validated_questions: List[Dict] = []
        for q in questions:
            if not isinstance(q, dict):
                continue
            question_text = q.get("question")
            category = q.get("category")
            difficulty = q.get("difficulty")
            if not question_text or not category or not difficulty:
                continue

            normalized_category = _normalize_category(str(category))
            normalized_difficulty = _normalize_difficulty(str(difficulty))
            if not normalized_category:
                logger.warning(f"Unknown category '{category}', skipping question")
                continue
            if not normalized_difficulty:
                logger.warning(f"Unknown difficulty '{difficulty}', skipping question")
                continue

            validated_questions.append(
                {
                    "category": normalized_category,
                    "difficulty": normalized_difficulty,
                    "question": str(question_text).strip(),
                }
            )

        insights = data.get("insights", {})
        if not isinstance(insights, dict):
            insights = {}

        ats_suggestions = data.get("ats_suggestions", [])
        if not isinstance(ats_suggestions, list):
            ats_suggestions = []

        return {
            "questions": validated_questions,
            "insights": insights,
            "ats_suggestions": ats_suggestions,
        }

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove markdown code fences from LLM JSON output."""
        return MARKDOWN_JSON_FENCE.sub("", text).strip()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError)
        ),
        reraise=True,
    )
    def _create_chat_completion(self, **kwargs: Any) -> Any:
        """Create a chat completion with retry on transient failures."""
        return self.client.chat.completions.create(**kwargs)

    def _build_system_prompt(self, resume_text: str) -> str:
        """Build a focused system prompt based on resume content."""
        # Extract a few keywords to tailor the system prompt without sending full resume
        keywords = []
        for keyword in [
            "Python",
            "Java",
            "JavaScript",
            "React",
            "AWS",
            "SQL",
            "Docker",
            "Kubernetes",
            "Machine Learning",
            "Data Science",
        ]:
            if keyword.lower() in resume_text.lower():
                keywords.append(keyword)

        tech_context = ", ".join(keywords) if keywords else "general technical skills"
        return (
            "You are an expert technical interviewer who creates relevant and insightful "
            f"interview questions based on candidate resumes. Focus on: {tech_context}. "
            "Ask questions that assess practical experience, problem-solving, and "
            "behavioral competencies relevant to the candidate's background."
        )

    def generate_questions(
        self,
        resume_text: str,
        question_count: int = 5,
        difficulty_filter: Optional[List[str]] = None,
        category_filter: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate interview questions, insights, and ATS suggestions based on resume content

        Args:
            resume_text: Resume content
            question_count: Number of questions to generate (max 10)
            difficulty_filter: List of difficulty levels to include
            category_filter: List of categories to include

        Returns:
            Dict: Complete response with questions, insights, and ATS suggestions
        """
        if difficulty_filter is None:
            difficulty_filter = ["Easy"]
        if category_filter is None:
            category_filter = ["Technical Skills"]

        # Validate filters against known constants
        invalid_difficulties = set(difficulty_filter) - VALID_DIFFICULTIES
        if invalid_difficulties:
            raise ValueError(f"Invalid difficulty levels: {invalid_difficulties}")

        invalid_categories = set(category_filter) - VALID_CATEGORIES
        if invalid_categories:
            raise ValueError(f"Invalid categories: {invalid_categories}")

        try:
            # Validate question count
            if question_count > 10:
                question_count = 10

            # Sanitize input
            sanitized_text = self._sanitize_resume_text(resume_text)

            # Handle coding test instructions
            coding_test_instruction = ""
            if "Coding Test" in category_filter:
                coding_test_instruction = (
                    "\n\nAdditionally, generate up to 2 LeetCode-style coding questions in Python for the 'Coding Test' category. "
                    "Each coding question should include: a clear problem statement, input/output format, at least 2 sample test cases, and difficulty based on the selected level. "
                    "Format the coding questions with a markdown code block for the function signature and test cases."
                )

            # Create the prompt for question generation
            prompt = (
                self._create_question_prompt(
                    sanitized_text, question_count, difficulty_filter, category_filter
                )
                + coding_test_instruction
            )

            # Generate questions using OpenAI with retry and structured JSON output
            response = self._create_chat_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._build_system_prompt(sanitized_text),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=4000,
                response_format={"type": "json_object"},
            )

            # Parse the complete response
            llm_response = response.choices[0].message.content

            if not llm_response or llm_response.strip() == "":
                return {"questions": [], "insights": {}, "ats_suggestions": []}

            # Strip markdown fences if present, then parse JSON
            cleaned_response = self._strip_markdown_fences(llm_response)
            try:
                data = json.loads(cleaned_response)
                return self._validate_response_shape(data)

            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.debug(f"Raw response: {cleaned_response[:500]}")
                return {"questions": [], "insights": {}, "ats_suggestions": []}

        except ValueError:
            raise
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise RuntimeError(
                "OpenAI rate limit exceeded. Please wait and try again."
            ) from e
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}")
            raise RuntimeError(
                "Unable to connect to OpenAI. Please check your internet connection."
            ) from e
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI request timed out: {e}")
            raise RuntimeError("OpenAI request timed out. Please try again.") from e
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise RuntimeError(f"Failed to generate questions: {str(e)}") from e

    def evaluate_answer(
        self,
        question: str,
        category: str,
        difficulty: str,
        candidate_answer: str,
        resume_context: Optional[str] = None,
    ) -> Dict:
        """
        Evaluate a candidate's answer to an interview question.

        Args:
            question: The interview question asked
            category: Question category
            difficulty: Question difficulty
            candidate_answer: Candidate's response text
            resume_context: Optional resume summary for context

        Returns:
            Dict: score (1-5), strengths, gaps, follow_up questions, feedback
        """
        if not candidate_answer or not candidate_answer.strip():
            return {
                "score": 0,
                "strengths": [],
                "gaps": ["No answer provided"],
                "follow_up": [],
                "feedback": "Please provide an answer before evaluating.",
            }

        context_section = ""
        if resume_context:
            context_section = f"\nRESUME CONTEXT:\n{resume_context[:2000]}"

        prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

QUESTION ({category}, {difficulty}):
{question}

CANDIDATE ANSWER:
{candidate_answer}
{context_section}

Evaluate the answer on correctness, depth, relevance, and communication clarity.
Provide a score from 1 to 5, list strengths, identify gaps/missing points, suggest 1-2 follow-up questions, and give brief overall feedback.

Respond ONLY with valid JSON:
{{
    "score": <integer 1-5>,
    "strengths": ["strength 1", "strength 2"],
    "gaps": ["gap 1", "gap 2"],
    "follow_up": ["follow-up question 1", "follow-up question 2"],
    "feedback": "brief overall feedback"
}}"""

        try:
            response = self._create_chat_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical interviewer evaluating candidate answers objectively and constructively.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=1000,
                response_format={"type": "json_object"},
            )

            llm_response = response.choices[0].message.content
            if not llm_response or llm_response.strip() == "":
                return {
                    "score": 0,
                    "strengths": [],
                    "gaps": ["Empty response from evaluation service"],
                    "follow_up": [],
                    "feedback": "Evaluation service returned no response.",
                }

            cleaned = self._strip_markdown_fences(llm_response)
            data = json.loads(cleaned)

            return {
                "score": int(data.get("score", 0)),
                "strengths": data.get("strengths", []),
                "gaps": data.get("gaps", []),
                "follow_up": data.get("follow_up", []),
                "feedback": str(data.get("feedback", "")),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Answer evaluation JSON error: {e}")
            return {
                "score": 0,
                "strengths": [],
                "gaps": ["Failed to parse evaluation response"],
                "follow_up": [],
                "feedback": f"Evaluation failed: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Answer evaluation error: {e}")
            return {
                "score": 0,
                "strengths": [],
                "gaps": [f"Evaluation error: {str(e)}"],
                "follow_up": [],
                "feedback": f"Evaluation failed: {str(e)}",
            }

    def _create_question_prompt(
        self,
        resume_text: str,
        question_count: int,
        difficulty_filter: List[str],
        category_filter: List[str],
    ) -> str:
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
{resume_text}

TASKS:
1. Generate {question_count} interview questions
2. Extract key insights
3. Provide ATS suggestions

REQUIREMENTS:
- Questions for categories: {', '.join(category_filter)}
- Difficulty levels: {', '.join(difficulty_filter)}
- Each question needs: category, difficulty, question text
- Reference technologies, tools, and domains from the resume, but do NOT copy verbatim project scenarios, specific company names, dollar amounts, or detailed case studies from the resume into the questions
- Make questions general enough that they test knowledge of the technology/tool rather than recall of a specific project the candidate worked on
- Avoid questions that assume the candidate did exactly what is described in the resume; instead ask how they would approach similar problems using the technologies they list

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


if __name__ == "__main__":
    pass
