"""
Interview Assistant - Main Application
Streamlit app for AI-powered interview question generation
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from interview_assistant.core.resume_parser import ResumeParser
from interview_assistant.core.question_generator import QuestionGenerator
from interview_assistant.utils.helpers import format_questions_for_export
import time

# Page configuration
st.set_page_config(
    page_title="Interview Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 2rem 0;
    }
    .question-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .difficulty-easy { border-left-color: #28a745; }
    .difficulty-medium { border-left-color: #ffc107; }
    .difficulty-hard { border-left-color: #dc3545; }
    .category-badge {
        background-color: #e9ecef;
        color: #495057;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.875rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Interview Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered interview question generator for technical roles</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Question count slider
        question_count = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=10,
            help="Select how many questions to generate (maximum 10)"
        )
        
        # Difficulty filter
        difficulty_filter = st.multiselect(
            "Difficulty Level",
            options=["Easy", "Medium", "Hard"],
            default=["Easy"],
            help="Select difficulty levels for questions (Easy: Basic knowledge, Medium: Practical experience, Hard: Advanced concepts)"
        )
        
        # Category filter
        category_filter = st.multiselect(
            "Question Categories",
            options=["Technical Skills", "Experience & Projects", "Problem Solving", "Behavioral"],
            default=["Technical Skills"],
            help="Select categories to focus on (Technical: Skills & tools, Experience: Past work, Problem Solving: Analytical thinking, Behavioral: Soft skills)"
        )
        
        # Validation
        if not difficulty_filter:
            st.error("⚠️ Please select at least one difficulty level")
        if not category_filter:
            st.error("⚠️ Please select at least one category")
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Upload a resume (PDF or Word format)
        2. Select number of questions (max 10)
        3. Choose difficulty levels and categories
        4. Click 'Generate Questions' button
        5. Review and export the generated questions
        """)
        
        # st.markdown("---")
        # st.markdown("### 🔧 Setup")
        # st.markdown("""
        # Make sure to set your OpenAI API key:
        # ```bash
        # export OPENAI_API_KEY=your_api_key_here
        # ```
        # """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Resume Upload")
        
        # File upload section
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx'],
            help="Upload a PDF or Word document containing the candidate's resume"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display file info
            file_details = {
                "Filename": uploaded_file.name,
                "File type": uploaded_file.type,
                "File size": f"{uploaded_file.size / 1024:.1f} KB"
            }
            st.json(file_details)
            
            # Parse resume
            with st.spinner("📖 Parsing resume..."):
                resume_text = ResumeParser.parse_resume(uploaded_file)
                
            if resume_text:
                st.success("✅ Resume parsed successfully!")
                
                                # Show resume preview
                with st.expander("📋 Resume Preview"):
                    # Show cleaned, formatted text
                    cleaned_preview = resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text
                    st.text_area("Cleaned Resume Content", cleaned_preview, height=200, help="Cleaned and formatted text that will be sent to the AI")
                    
                    # Show text statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Characters", len(resume_text))
                    with col2:
                        st.metric("Words", len(resume_text.split()))
                    with col3:
                        st.metric("Lines", resume_text.count('\n') + 1)
                
                # Generate questions button
                if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
                    if not difficulty_filter:
                        st.error("⚠️ Please select at least one difficulty level")
                    elif not category_filter:
                        st.error("⚠️ Please select at least one category")
                    elif question_count > 10:
                        st.error("⚠️ Question count cannot exceed 10")
                    else:
                        generate_questions(resume_text, question_count, difficulty_filter, category_filter)
                
                # Display generated questions below the button
                if 'questions' in st.session_state and st.session_state.questions:
                    st.markdown("---")
                    st.subheader("🎯 Generated Questions")
                    display_questions(st.session_state.questions, difficulty_filter, category_filter)
                

    
    with col2:
        st.header("📊 Question Statistics")
        
        # Show summary info
        if 'questions' in st.session_state and st.session_state.questions:
            questions = st.session_state.questions
            categories = {}
            for question in questions:
                category = question['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(question)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", len(questions))
            with col2:
                st.metric("Categories", len(categories))
            with col3:
                hard_count = sum(1 for q in questions if q['difficulty'] == 'Hard')
                st.metric("Hard Questions", hard_count)
            
            # Show category breakdown
            st.markdown("---")
            st.subheader("📂 Category Breakdown")
            for category, category_questions in categories.items():
                st.write(f"**{category}**: {len(category_questions)} questions")
        else:
            st.info("👆 Upload a resume and click 'Generate Questions' to see statistics!")

def generate_questions(resume_text: str, question_count: int, difficulty_filter: list, category_filter: list):
    """Generate interview questions using OpenAI"""
    
    with st.spinner("🤖 Generating questions with AI..."):
        # Initialize question generator
        generator = QuestionGenerator()
        
        # Generate questions
        questions = generator.generate_questions(resume_text, question_count, difficulty_filter, category_filter)
        
        if questions:
            # Store questions in session state
            st.session_state.questions = questions
            st.success(f"✅ Generated {len(questions)} questions!")
            
            # Rerun to display questions
            st.rerun()
        else:
            st.error("❌ Failed to generate questions. Please check your OpenAI API key and try again.")

def display_questions(questions: list, difficulty_filter: list, category_filter: list):
    """Display generated questions with filtering"""
    
    filtered_questions = questions
    if not filtered_questions:
        st.warning("No questions match the current filters. Try adjusting the filter settings.")
        return
    

    
    # Display questions by category
    categories = {}
    for question in filtered_questions:
        category = question['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(question)
    

    
    # Display questions by category
    for category, category_questions in categories.items():
        st.subheader(f"📂 {category}")
        
        for i, question in enumerate(category_questions, 1):
            difficulty_class = f"difficulty-{question['difficulty'].lower()}"
            
            st.markdown(f"""
            <div class="question-card {difficulty_class}">
                <div style="display: flex; justify-content: end; align-items: center; margin-bottom: 0.5rem;">
                    <span class="category-badge" style="background-color: {'#d4edda' if question['difficulty'] == 'Easy' else '#fff3cd' if question['difficulty'] == 'Medium' else '#f8d7da'}; color: {'#155724' if question['difficulty'] == 'Easy' else '#856404' if question['difficulty'] == 'Medium' else '#721c24'};">
                        {question['difficulty']}
                    </span>
                </div>
                <p style="margin: 0; font-size: 1.1rem;"><strong>{i}.</strong> {question['question']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Export options
    st.markdown("---")
    st.subheader("📤 Export Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as CSV", use_container_width=True):
            export_to_csv(filtered_questions)
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            export_to_clipboard(filtered_questions)

def export_to_csv(questions: list):
    """Export questions to CSV format"""
    df = pd.DataFrame(questions)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="💾 Download CSV",
        data=csv,
        file_name="interview_questions.csv",
        mime="text/csv"
    )

def export_to_clipboard(questions: list):
    """Export questions to clipboard-friendly format"""
    formatted_text = format_questions_for_export(questions)
    
    st.text_area("Copy the questions below:", formatted_text, height=300)
    st.success("📋 Questions formatted for clipboard!")

if __name__ == "__main__":
    main() 