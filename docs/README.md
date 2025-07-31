# Interview Assistant Documentation

## Overview

The Interview Assistant is an AI-powered tool that generates relevant interview questions based on candidate resumes. This document provides detailed information about the project structure, architecture, and usage.

## Architecture

### Project Structure

```
interview-assisst/
├── src/
│   └── interview_assistant/
│       ├── __init__.py
│       ├── main.py              # Main application entry point
│       ├── core/                # Core business logic
│       │   ├── __init__.py
│       │   ├── resume_parser.py # Resume text extraction
│       │   └── question_generator.py # AI question generation
│       ├── utils/               # Utility functions
│       │   ├── __init__.py
│       │   └── helpers.py       # Helper functions
│       └── ui/                  # User interface components
│           ├── __init__.py
│           └── streamlit_app.py # Streamlit UI components
├── tests/                       # Test suite
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── config/                      # Configuration files
├── pyproject.toml              # Poetry configuration
├── requirements.txt            # Dependencies
└── README.md                   # Project overview
```

### Core Components

#### 1. Resume Parser (`core/resume_parser.py`)
- Extracts text from PDF and Word documents
- Handles different file formats and error cases
- Returns clean text for AI processing

#### 2. Question Generator (`core/question_generator.py`)
- Integrates with OpenAI API
- Generates contextual interview questions
- Categorizes questions by type and difficulty

#### 3. Utilities (`utils/helpers.py`)
- Skill extraction from text
- Experience level estimation
- Resume scoring algorithms
- File validation functions

#### 4. Main Application (`main.py`)
- Streamlit application logic
- User interface management
- Question display and export functionality

## API Reference

### ResumeParser

```python
class ResumeParser:
    @staticmethod
    def parse_resume(uploaded_file) -> Optional[str]:
        """Parse resume file and extract text."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> Optional[str]:
        """Extract text from PDF file."""
    
    @staticmethod
    def extract_text_from_docx(docx_file) -> Optional[str]:
        """Extract text from Word document."""
```

### QuestionGenerator

```python
class QuestionGenerator:
    def __init__(self):
        """Initialize with OpenAI API key."""
    
    def generate_questions(self, resume_text: str, question_count: int = 10) -> List[Dict]:
        """Generate interview questions based on resume content."""
```

### Utility Functions

```python
def extract_skills_from_text(text: str) -> List[str]:
    """Extract technical skills from resume text."""

def estimate_experience_level(text: str) -> str:
    """Estimate candidate experience level."""

def calculate_resume_score(text: str) -> Dict[str, float]:
    """Calculate various scores for the resume."""

def validate_file_upload(uploaded_file) -> bool:
    """Validate uploaded file format and size."""
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
OPENAI_MODEL=gpt-4-1106-preview
```

### Poetry Configuration

The project uses Poetry for dependency management. Key configuration in `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.10"
streamlit = "^1.28.1"
openai = "^1.3.7"
# ... other dependencies

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.5.0"
pre-commit = "^3.3.0"
```

## Development

### Setup

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp env_example.txt .env
   # Edit .env with your OpenAI API key
   ```

4. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

### Running the Application

```bash
# Using Poetry
poetry run streamlit run src/interview_assistant/main.py

# Or activate the environment first
poetry shell
streamlit run src/interview_assistant/main.py
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=interview_assistant

# Run specific test file
poetry run pytest tests/test_core.py
```

### Code Quality

```bash
# Format code
poetry run black .

# Lint code
poetry run flake8 .

# Type checking
poetry run mypy .

# Run all checks
make check
```

## Deployment

### Local Development
```bash
poetry run streamlit run src/interview_assistant/main.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in Streamlit Cloud dashboard
4. Deploy

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8501

CMD ["streamlit", "run", "src/interview_assistant/main.py"]
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure `OPENAI_API_KEY` is set in environment variables
   - Check API key validity in OpenAI dashboard

2. **File Upload Issues**
   - Only PDF and Word documents are supported
   - Maximum file size is 10MB

3. **Dependency Issues**
   - Use Poetry for dependency management
   - Ensure Python version is 3.10 or higher

### Performance Optimization

- Use smaller resume files for faster processing
- Limit question count to reduce API costs
- Use specific category filters to focus on relevant areas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run code quality checks
6. Submit a pull request

## License

This project is licensed under the MIT License. 