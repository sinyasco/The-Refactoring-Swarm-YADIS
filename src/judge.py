import json
import os
import subprocess
from langchain_google_genai import ChatGoogleGenerativeAI

class Judge:
    def __init__(self, gemini_key):
        self.gemini_key = gemini_key
    
    def run_tests(self, file_path):
        """
        Runs pylint on the file and uses AI to judge the results.
        Returns (success: bool, logs: str)
        """
        # Run pylint on the file
        try:
            result = subprocess.run(
                ["pylint", file_path, "--output-format=text"],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            test_output = "Pylint timed out"
        except FileNotFoundError:
            test_output = "Pylint not found"
        
        # Read the judge prompt
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'judge_prompt_v1.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Combine prompt with test output
        full_prompt = f"{prompt_template}\n\nTest output:\n{test_output}"
        
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=self.gemini_key)
        
        # Get response
        response = llm.invoke(full_prompt)
        response_text = response.content.strip()
        
        # Parse JSON response
        try:
            judgment = json.loads(response_text)
            status = judgment.get("status", "FAILURE")
            success = status == "SUCCESS"
            logs = test_output
            return success, logs
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response from Judge: {e}")
            return False, f"Judgment failed: {test_output}"