import os
from openai import OpenAI

def load_resume_text(resume_path="tushar/tushar_resume.txt"):
    """Load resume content from a text file."""
    try:
        with open(resume_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading resume: {e}"


def chat_with_resume_context(user_input: str, client: OpenAI, resume_text: str):
    """
    Sends message to OpenAI with resume context and retrieves answer.
    """
    try:
        prompt = f"""
You are Tushar's AI assistant. Answer questions ONLY based on the following resume text:

{resume_text}

Question: {user_input}
Answer concisely and professionally.
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # cheaper & sufficient
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip(), True
    except Exception as e:
        return f"Try more specific questions. Like 'Tell me about his experience' or 'What are his skills?'", False
