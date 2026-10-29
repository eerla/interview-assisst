# 🎯 Interview Assistant for IT Technical Roles

An AI-powered interview question generator that helps interviewers prepare relevant questions based on candidate resumes. Built with Streamlit and OpenAI's GPT models.

## 🚀 Features

- **📄 Resume Parsing**: Supports PDF and Word document formats
- **🤖 AI-Powered Questions**: Generates contextual interview questions using OpenAI GPT
- **📊 Question Categorization**: Organizes questions by Technical Skills, Experience & Projects, Problem Solving, and Behavioral
- **🎯 Difficulty Levels**: Questions are generated with specified difficulty levels (Easy, Medium, Hard)
- **🔍 Smart Filtering**: Filter questions by category and difficulty level
- **📤 Export Options**: Export questions as CSV or copy to clipboard
- **🎨 Modern UI**: Beautiful, responsive interface built with Streamlit
- **⚡ Real-time Analysis**: Instant resume parsing and question generation
- **🎯 Simplified Generation**: Clean, focused prompts ensure consistent question format and quality

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- OpenAI API key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd interview-assisst
```

### 2. Install Dependencies

**Option A: Using Poetry (Recommended)**
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

**Option B: Using pip (Alternative)**
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
# Copy the example file
cp env_example.txt .env

# Edit .env file and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-1106-preview
```

### 4. Run the Application

**With Poetry:**
```bash
poetry run streamlit run run_app.py
```

**With pip:**
```bash
streamlit run run_app.py
```

The application will open in your browser at `http://localhost:8501`

### 🐳 Docker Deployment

Build and run with Docker:

```bash
docker build -t interview-assistant .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key interview-assistant
```

Or with docker-compose:

```yaml
services:
  interview-assistant:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=your_openai_api_key
      - OPENAI_MODEL=gpt-4-1106-preview
```

## 📖 Usage Guide

### 1. Upload Resume
- Click "Browse files" to upload a PDF or Word document
- Supported formats: `.pdf`, `.docx`
- Maximum file size: 10MB

### 2. Configure Settings
Use the sidebar to customize:
- **Number of Questions**: Choose between 1-10 questions (maximum 10)
- **Difficulty Level**: Filter by Easy, Medium, or Hard
- **Question Categories**: Select specific categories to focus on

### 3. Generate Questions
- Click the "🚀 Generate Questions" button
- Wait for AI processing (usually 10-30 seconds)
- Review the generated questions organized by category

### 4. Export Results
- **CSV Export**: Download questions as a spreadsheet
- **Clipboard Copy**: Copy formatted questions to clipboard

## 🏗️ Project Structure

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

## 🔧 Technical Details

### Resume Parsing
- **PDF Processing**: Uses PyPDF2 for text extraction
- **Word Documents**: Uses python-docx for .docx files
- **Error Handling**: Robust error handling for corrupted or unsupported files

### Question Generation
- **OpenAI Integration**: Uses GPT-3.5-turbo or GPT-4 for question generation
- **Prompt Engineering**: Carefully crafted prompts for relevant, contextual questions
- **Token Management**: Optimized to manage API costs and response quality

### Question Categorization
- **Technical Skills**: Programming languages, frameworks, tools
- **Experience & Projects**: Work history, project details, achievements
- **Problem Solving**: Scenario-based and analytical questions
- **Behavioral**: Teamwork, leadership, communication skills

## 🎨 UI Features

- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Feedback**: Progress indicators and status messages
- **Interactive Filters**: Dynamic question filtering and sorting
- **Export Options**: Multiple formats for question export
- **Modern Styling**: Clean, professional interface with custom CSS

## 🔒 Security & Privacy

- **Local Processing**: Resume files are processed locally
- **No Data Storage**: Files are not stored permanently
- **API Security**: OpenAI API key is handled securely via environment variables
- **File Validation**: Comprehensive file type and size validation

## 🚀 Deployment

### Local Development
```bash
poetry run streamlit run run_app.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables (`OPENAI_API_KEY`, `OPENAI_MODEL`) in Streamlit Cloud dashboard
4. Deploy

### Docker Deployment
Build the image and run:

```bash
docker build -t interview-assistant .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key interview-assistant
```

The Dockerfile at the project root provides a production-ready container based on `python:3.11-slim`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**OpenAI API Key Error**
```
Error: OpenAI API key not found
```
Solution: Ensure your `.env` file contains the correct API key

**File Upload Issues**
```
Error: Unsupported file format
```
Solution: Only PDF (.pdf) and Word (.docx) files are supported

**Question Generation Fails**
```
Error: Failed to generate questions
```
Solution: Check your internet connection and OpenAI API key validity

### Performance Tips

- Use smaller resume files for faster processing
- Limit question count to reduce API costs
- Use specific category filters to focus on relevant areas

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the project documentation
3. Open an issue on GitHub

---

**Built with ❤️ using Streamlit and OpenAI**