#!/usr/bin/env python3
"""
Test script to verify difficulty estimation improvements
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interview_assistant.core.question_generator import QuestionGenerator

def test_difficulty_estimation():
    """Test the improved difficulty estimation"""
    
    generator = QuestionGenerator()
    
    # Test questions for different categories and difficulties
    test_cases = [
        # Technical Skills
        ("What is Python?", "Technical Skills", "Easy"),
        ("How would you implement a binary search tree?", "Technical Skills", "Medium"),
        ("Design a distributed caching system", "Technical Skills", "Hard"),
        
        # Experience & Projects
        ("Describe your last project", "Experience & Projects", "Easy"),
        ("What was your role in the team?", "Experience & Projects", "Medium"),
        ("How did you handle a critical system failure?", "Experience & Projects", "Hard"),
        
        # Problem Solving
        ("What would you do if a server is down?", "Problem Solving", "Easy"),
        ("How would you debug a memory leak?", "Problem Solving", "Medium"),
        ("Design a system to handle 1 million concurrent users", "Problem Solving", "Hard"),
        
        # Behavioral
        ("Tell me about yourself", "Behavioral", "Easy"),
        ("How do you handle feedback?", "Behavioral", "Medium"),
        ("Describe a time you had to lead through a crisis", "Behavioral", "Hard"),
    ]
    
    print("🧪 Testing Difficulty Estimation")
    print("=" * 50)
    
    correct = 0
    total = 0
    
    for question, category, expected in test_cases:
        estimated = generator._estimate_difficulty(question, category)
        status = "✅" if estimated == expected else "❌"
        print(f"{status} {category}: {question}")
        print(f"   Expected: {expected}, Got: {estimated}")
        print()
        
        if estimated == expected:
            correct += 1
        total += 1
    
    print(f"📊 Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
    
    # Test difficulty extraction from marked text
    print("\n🔍 Testing Difficulty Extraction")
    print("=" * 50)
    
    marked_questions = [
        "[EASY] What is Python?",
        "[MEDIUM] How would you implement a binary search?",
        "[HARD] Design a distributed system",
        "No marker question"
    ]
    
    for question in marked_questions:
        difficulty = generator._extract_difficulty_from_text(question)
        clean_text = generator._clean_question_text(question)
        print(f"Original: {question}")
        print(f"Difficulty: {difficulty}")
        print(f"Cleaned: {clean_text}")
        print()

if __name__ == "__main__":
    test_difficulty_estimation() 