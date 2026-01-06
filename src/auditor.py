class Auditor:
    def analyze(self, file_path, gemini_key=None):
        """
        Reads code and generates a dummy refactoring plan.
        """
        print(f"Auditor analyzing {file_path} (Gemini key loaded: {bool(gemini_key)})")
        plan = {"file": file_path, "issues": ["dummy_issue"]}
        return plan