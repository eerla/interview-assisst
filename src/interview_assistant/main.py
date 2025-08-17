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
        background-color: black;
        padding: 0.5rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        color: white;
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
    .category-badge.easy {
        background-color: #d4edda !important; /* light green */
        color: #155724 !important;
    }
    .category-badge.medium {
        background-color: #fff3cd !important; /* light yellow */
        color: #856404 !important;
    }
    .category-badge.hard {
        background-color: #f8d7da !important; /* light red */
        color: #721c24 !important;
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
            options=["Technical Skills", "Experience & Projects", "Problem Solving", "Behavioral", "Coding Test"],
            default=["Technical Skills"],
            help="Select categories to focus on (Technical: Skills & tools, Experience: Past work, Problem Solving: Analytical thinking, Behavioral: Soft skills, Coding Test: LeetCode-style coding questions)"
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
    col1, col2 = st.columns([1, 0.5])
    
    with col1:
        st.header("📄 Resume Upload")
        
        # File upload section
        # st.markdown('<div class="upload-section">', unsafe_allow_html=True)
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
                    display_questions(st.session_state.questions)
                

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
        generator = QuestionGenerator()
        try:
            coding_test_selected = "Coding Test" in category_filter
            coding_test_instruction = ""
            if coding_test_selected:
                coding_test_instruction = (
                    "\n\nAdditionally, generate up to 2 LeetCode-style coding questions in Python for the 'Coding Test' category. "
                    "Each coding question should include: a clear problem statement, input/output format, at least 2 sample test cases, and difficulty based on the selected level. "
                    "Format the coding questions with a markdown code block for the function signature and test cases."
                )
            prompt = generator._create_question_prompt(resume_text, question_count, difficulty_filter, category_filter) + coding_test_instruction
            response = generator.client.chat.completions.create(
                model=generator.model,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who creates relevant and insightful interview questions based on candidate resumes. You are also expert in python, pyspark, java, c++, c, javascript, html, css, sql databases, nosql databases, data structures, data modeling, algorithms, system design, microservices, distributed systems, cloud computing, artificial intelligence, machine learning, deep learning, natural language processing, computer vision, robotics, and other related technologies. You are also expert in data analysis, data visualization, data engineering, data science, data warehousing, data modeling, data cleaning, data integration, data transformation, data loading, data unloading, data archiving, data backup, data recovery, data replication, data synchronization, data migration, REST APIs, CICD pipelines, and other related technologies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            llm_response = response.choices[0].message.content
            questions = generator._parse_questions(llm_response)
            insights = generator._parse_insights(llm_response)
            ats_suggestions = generator._parse_ats_suggestions(llm_response)
            st.session_state.questions = questions
            st.session_state.resume_insights = insights
            st.session_state.ats_suggestions = ats_suggestions
            st.success(f"✅ Generated {len(questions)} questions!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to generate questions and insights: {e}")

def display_questions(questions: list):
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
            difficulty_badge_class = f"category-badge {question['difficulty'].lower()}"
            if category == "Coding Test":
                st.markdown(f"""
                <div class="question-card {difficulty_class}">
                    <div style="display: flex; justify-content: end; align-items: center; margin-bottom: 0.5rem;">
                        <span class="{difficulty_badge_class}">{question['difficulty']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**{i}. {question['question']}**")
                if 'instructions' in question:
                    st.markdown(question['instructions'])
                if 'test_cases' in question:
                    st.markdown("**Sample Test Cases:**")
                    for tc in question['test_cases']:
                        st.code(tc, language="python")
            else:
                st.markdown(f"""
                <div class="question-card {difficulty_class}">
                    <div style="display: flex; justify-content: end; align-items: center; margin-bottom: 0.5rem;">
                        <span class="{difficulty_badge_class}">
                            {question['difficulty']}
                        </span>
                    </div>
                    <p style="margin: 0; font-size: 1.1rem;"><strong>{i}.</strong> {question['question']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    if 'resume_insights' in st.session_state and st.session_state.resume_insights:
        st.markdown("---")
        st.subheader("🔑 Resume Key Insights")
        display_resume_insights(st.session_state.resume_insights)
    if 'ats_suggestions' in st.session_state and st.session_state.ats_suggestions:
        st.markdown("---")
        st.subheader("📝 ATS Optimization Suggestions")
        display_ats_suggestions(st.session_state.ats_suggestions)

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

def display_resume_insights(insights: dict):
    """Display extracted resume insights in a structured format."""
    if not insights:
        st.info("No insights extracted from resume.")
        return
    if 'technologies' in insights:
        st.markdown(f"**Technologies/Skills:** {', '.join(insights['technologies']) if insights['technologies'] else 'N/A'}")
    if 'companies' in insights and insights['companies']:
        st.markdown("**Companies & Durations:**")
        for c in insights['companies']:
            st.markdown(f"- {c.get('name', 'Unknown')} ({c.get('duration', 'N/A')})")
    if 'total_years_experience' in insights:
        st.markdown(f"**Total Years Experience:** {insights['total_years_experience']}")
    if 'education' in insights and insights['education']:
        st.markdown("**Education:**")
        for edu in insights['education']:
            st.markdown(f"- {edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})")
    if 'certifications' in insights and insights['certifications']:
        st.markdown(f"**Certifications:** {', '.join(insights['certifications'])}")
    if 'major_projects' in insights and insights['major_projects']:
        st.markdown("**Major Projects:**")
        for proj in insights['major_projects']:
            st.markdown(f"- {proj}")

def display_ats_suggestions(suggestions: list):
    """Display ATS optimization suggestions."""
    if not suggestions:
        st.info("No ATS suggestions available.")
        return
    st.markdown("**Suggestions to improve ATS compatibility:**")
    for s in suggestions:
        st.markdown(f"- {s}")
        
if __name__ == "__main__":
    main() 