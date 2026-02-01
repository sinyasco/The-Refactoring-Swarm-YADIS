import json
import os
from groq import Groq

class Fixer:
    def __init__(self, groq_key):
        self.groq_key = groq_key
    
    def apply_fix(self, plan):
        """
        Applies fixes to the Python file based on the refactoring plan using Groq AI.
        """
        file_path = plan["file"]
        
        # Read the original code
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Read the fixer prompt
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'fixer_prompt_v1.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Prepare the input: prompt + original code + plan
        plan_json = json.dumps(plan, indent=2)
        full_prompt = f"{prompt_template}\n\nOriginal Python file:\n{original_code}\n\nRefactoring plan:\n{plan_json}"
        
        # Initialize Groq client
        client = Groq(api_key=self.groq_key)
        
        # Get response from Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful code refactoring assistant. Return only the fixed Python code without any explanations, markdown formatting, or additional text. Just pure Python code."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # Fast and capable model
            temperature=0.1,
            max_tokens=4096
        )
        
        fixed_code = chat_completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code.split("```python", 1)[1]
            fixed_code = fixed_code.rsplit("```", 1)[0].strip()
        elif fixed_code.startswith("```"):
            fixed_code = fixed_code.split("```", 1)[1]
            fixed_code = fixed_code.rsplit("```", 1)[0].strip()
        
        # Write the fixed code back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        print(f"Fixer applied fixes to {file_path}")
        return plan
