import os
import json
from groq import Groq


class Tester:
    """
    Tester Agent — generates unit tests for a Python file using Groq AI.
    Follows TDD: writes tests that may initially fail, then the Fixer repairs
    the code until the Judge confirms all tests pass.
    """

    def __init__(self, groq_key: str):
        self.groq_key = groq_key

    def generate_tests(self, file_path: str, plan: dict | None = None) -> str:
        """
        Generates a unit-test file for *file_path* and writes it next to the
        source file as  test_<filename>.py.

        Returns the path of the generated test file.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        filename = os.path.basename(file_path)
        module_name = os.path.splitext(filename)[0]
        test_file_path = os.path.join(
            os.path.dirname(file_path), f"test_{filename}"
        )

        # Build the prompt
        plan_section = ""
        if plan:
            plan_section = f"\n\nRefactoring plan (known issues to test for):\n{json.dumps(plan, indent=2)}"

        prompt = f"""You are an expert Python test engineer following TDD principles.

Given the Python source file below, generate a comprehensive pytest test file that:
1. Tests ALL public functions and classes.
2. Covers normal cases, edge cases, and error cases.
3. Uses only the Python standard library and pytest — no extra dependencies.
4. Imports the module using:  from {module_name} import *
5. Each test function must have a clear docstring explaining what it checks.
6. If the source contains obvious bugs, write tests that EXPOSE those bugs
   (they will fail now and pass after the Fixer corrects the code).

Return ONLY valid Python code for the test file — no markdown, no explanations.{plan_section}

Source file ({filename}):
{source_code}
"""

        client = Groq(api_key=self.groq_key)

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Python test engineer. "
                        "Return only valid Python pytest code, nothing else."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=4096,
        )

        test_code = response.choices[0].message.content.strip()

        # Strip markdown fences if the model added them
        if test_code.startswith("```python"):
            test_code = test_code.split("```python", 1)[1]
            test_code = test_code.rsplit("```", 1)[0].strip()
        elif test_code.startswith("```"):
            test_code = test_code.split("```", 1)[1]
            test_code = test_code.rsplit("```", 1)[0].strip()

        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        print(f"  🧪 Tester wrote: {test_file_path}")
        return test_file_path