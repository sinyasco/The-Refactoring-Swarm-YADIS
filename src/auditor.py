import json
import os
from groq import Groq

class Auditor:
    def analyze(self, file_path, groq_key=None):
        """
        Analyzes the Python file for issues using Groq AI.
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
        
        # Initialize Groq client
        client = Groq()
        
        # Get response from Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful code analysis assistant that provides structured JSON responses. Always return valid JSON only, without any markdown formatting or additional text."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # Fast and capable model
            temperature=0.2,
            max_tokens=2048
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.split("```json", 1)[1]
            response_text = response_text.rsplit("```", 1)[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```", 1)[1]
            response_text = response_text.rsplit("```", 1)[0].strip()
        
        # Parse JSON response
        try:
            plan = json.loads(response_text)
            plan["file"] = file_path  # Add file path to plan
            return plan
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response_text[:200]}...")
            return {"file": file_path, "issues": [], "error": "Failed to parse response"}
