#!/usr/bin/env python3
"""
Entry point for the Interview Assistant Streamlit application.
This script can be run directly with: streamlit run run_app.py
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import and run the main application
from interview_assistant.main import main

if __name__ == "__main__":
    main() 