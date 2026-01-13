import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI

class Auditor:
    def analyze(self, file_path, gemini_key=None):
        """
        Analyzes the Python file for issues using Gemini AI.
        """
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Read the auditor prompt
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'auditor_prompt_v1.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Combine prompt with code
        full_prompt = f"{prompt_template}\n\nPython code to analyze:\n{code_content}"
        
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_key)
        
        # Get response
        response = llm.invoke(full_prompt)
        response_text = response.content.strip()
        
        # Parse JSON response
        try:
            plan = json.loads(response_text)
            plan["file"] = file_path  # Add file path to plan
            return plan
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"file": file_path, "issues": [], "error": "Failed to parse response"}