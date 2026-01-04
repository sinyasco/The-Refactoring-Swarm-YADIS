class Judge:
    def run_tests(self, file_path):
        """
        Runs dummy unit tests.
        Returns (success: bool, logs: str)
        """
        print(f"Judge testing {file_path}")
        success = True  # always succeed in stub
        logs = "All tests passed (stub)"
        return success, logs