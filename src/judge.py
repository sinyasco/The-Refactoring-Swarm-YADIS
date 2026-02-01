import os
import subprocess

class Judge:
    def __init__(self, groq_key):
        self.groq_key = groq_key
    
    def run_tests(self, file_path):
        """
        Runs unit tests for the given Python file.
        Returns (success: bool, logs: str)
        
        The Judge looks for test files in common patterns:
        - test_<filename>.py
        - <filename>_test.py
        - tests/ directory
        """
        # Get the directory and filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        filename_no_ext = os.path.splitext(filename)[0]
        
        # Look for test files in common patterns
        test_patterns = [
            os.path.join(directory, f"test_{filename}"),
            os.path.join(directory, f"{filename_no_ext}_test.py"),
            os.path.join(directory, "tests", f"test_{filename}"),
            os.path.join(directory, "tests", f"{filename_no_ext}_test.py"),
            os.path.join(os.path.dirname(directory), "tests", f"test_{filename}"),
        ]
        
        test_file = None
        for pattern in test_patterns:
            if os.path.exists(pattern):
                test_file = pattern
                break
        
        if not test_file:
            # No test file found - try running pytest/unittest on the directory
            return self._run_pytest_or_unittest(directory, file_path)
        
        # Run the specific test file
        return self._run_test_file(test_file)
    
    def _run_test_file(self, test_file):
        """Run a specific test file using pytest or unittest."""
        # Try pytest first
        try:
            result = subprocess.run(
                ["pytest", test_file, "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_output = result.stdout + result.stderr
            success = result.returncode == 0
            return success, test_output
        except FileNotFoundError:
            pass  # pytest not installed, try unittest
        except subprocess.TimeoutExpired:
            return False, "Tests timed out"
        
        # Try unittest
        try:
            result = subprocess.run(
                ["python", "-m", "unittest", test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_output = result.stdout + result.stderr
            success = result.returncode == 0
            return success, test_output
        except subprocess.TimeoutExpired:
            return False, "Tests timed out"
        except Exception as e:
            return False, f"Failed to run tests: {str(e)}"
    
    def _run_pytest_or_unittest(self, directory, file_path):
        """Run pytest or unittest discovery on the directory."""
        # Try pytest discovery
        try:
            result = subprocess.run(
                ["pytest", directory, "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_output = result.stdout + result.stderr
            
            # Check if any tests were found
            if "no tests ran" in test_output.lower() or "collected 0 items" in test_output.lower():
                return self._fallback_syntax_check(file_path)
            
            success = result.returncode == 0
            return success, test_output
        except FileNotFoundError:
            pass  # pytest not installed
        except subprocess.TimeoutExpired:
            return False, "Tests timed out"
        
        # Try unittest discovery
        try:
            result = subprocess.run(
                ["python", "-m", "unittest", "discover", "-s", directory, "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            test_output = result.stdout + result.stderr
            
            # Check if any tests were found
            if "Ran 0 tests" in test_output:
                return self._fallback_syntax_check(file_path)
            
            success = result.returncode == 0
            return success, test_output
        except subprocess.TimeoutExpired:
            return False, "Tests timed out"
        except Exception as e:
            return self._fallback_syntax_check(file_path)
    
    def _fallback_syntax_check(self, file_path):
        """
        Fallback when no unit tests are found.
        At minimum, check if the Python file has valid syntax.
        """
        try:
            # Try to compile the Python file
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            compile(code, file_path, 'exec')
            
            # If it compiles, return success with a note
            return True, f"✅ No unit tests found, but {os.path.basename(file_path)} has valid Python syntax."
        except SyntaxError as e:
            return False, f"❌ Syntax Error: {str(e)}"
        except Exception as e:
            return False, f"❌ Error checking file: {str(e)}"
