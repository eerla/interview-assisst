#!/usr/bin/env python3
"""
Entry point for the Interview Assistant Streamlit application.
This script can be run directly with: streamlit run run_app.py
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from interview_assistant.main import main

if __name__ == "__main__":
    main() 