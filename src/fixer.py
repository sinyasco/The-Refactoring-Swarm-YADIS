import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI

class Fixer:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
    
    def apply_fix(self, plan):
        """
        Applies fixes to the Python file based on the refactoring plan using Gemini AI.
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
        
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=self.gemini_key)
        
        # Get response
        response = llm.invoke(full_prompt)
        fixed_code = response.content.strip()
        
        # Write the fixed code back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        print(f"Fixer applied fixes to {file_path}")
        return plan