#!/usr/bin/env python3
"""
Test script for the simplified question generator
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interview_assistant.core.question_generator import QuestionGenerator

def test_simplified_generator():
    """Test the simplified question generator"""
    
    print("🧪 Testing Simplified Question Generator")
    print("=" * 50)
    
    # Test data
    test_resume = """
    John Doe is a Senior Software Engineer with 8 years of experience in Python, Java, and cloud technologies.
    He has worked on large-scale distributed systems at Google and Amazon, specializing in microservices architecture.
    John has experience with AWS, Docker, Kubernetes, and has led teams of 5-10 developers.
    """
    
    # Test cases
    test_cases = [
        {
            "name": "Basic test - 5 questions, Easy difficulty, Technical Skills",
            "count": 5,
            "difficulty": ["Easy"],
            "category": ["Technical Skills"]
        },
        {
            "name": "Multiple difficulties and categories",
            "count": 8,
            "difficulty": ["Easy", "Medium", "Hard"],
            "category": ["Technical Skills", "Experience & Projects"]
        },
        {
            "name": "Maximum questions test",
            "count": 10,
            "difficulty": ["Medium"],
            "category": ["Problem Solving"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Create generator instance
            generator = QuestionGenerator()
            
            # Generate questions
            questions = generator.generate_questions(
                test_resume,
                test_case['count'],
                test_case['difficulty'],
                test_case['category']
            )
            
            # Display results
            print(f"✅ Generated {len(questions)} questions")
            print(f"📊 Expected: {test_case['count']}, Actual: {len(questions)}")
            
            if questions:
                print("\n📝 Sample questions:")
                for j, q in enumerate(questions[:3], 1):  # Show first 3
                    print(f"  {j}. [{q['difficulty']}] {q['category']}: {q['question'][:80]}...")
            
            # Validate results
            if len(questions) <= test_case['count']:
                print("✅ Question count validation: PASSED")
            else:
                print("❌ Question count validation: FAILED - Generated more than requested")
                
            # Validate difficulty levels
            valid_difficulties = all(q['difficulty'] in test_case['difficulty'] for q in questions)
            if valid_difficulties:
                print("✅ Difficulty validation: PASSED")
            else:
                print("❌ Difficulty validation: FAILED - Invalid difficulty levels found")
                
            # Validate categories
            valid_categories = all(q['category'] in test_case['category'] for q in questions)
            if valid_categories:
                print("✅ Category validation: PASSED")
            else:
                print("❌ Category validation: FAILED - Invalid categories found")
                
        except Exception as e:
            print(f"❌ Error in test case {i}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   This test will fail when trying to generate questions.")
        print("   Set your API key: export OPENAI_API_KEY=your_key_here")
        print()
    
    test_simplified_generator() 