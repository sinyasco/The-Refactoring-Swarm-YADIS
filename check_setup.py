import sys
import os

PYTHON_VERSION_MAJOR = 3
PYTHON_VERSION_MINOR = [10, 11]
ENV_FILE = ".env"
API_KEY_VARIABLE = "GROQ_API_KEY"
LOGS_DIR = "logs"

def check_environment():
    """
    Performs a sanity check on the environment to ensure it is set up correctly.
    """
    print("Starting 'Sanity Check'...\n")
    all_good = True

    try:
        # 1. Vérification Python
        version = sys.version_info
        if (version.major == PYTHON_VERSION_MAJOR) and (version.minor in PYTHON_VERSION_MINOR):
            print(f"Python Version: {version.major}.{version.minor}")
        else:
            print(f"Python Version: {version.major}.{version.minor} (Required: 3.10 or 3.11)")
            all_good = False
    except OSError as e:
        print(f"An OS error occurred: {e}")
        all_good = False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        all_good = False

    # 2. Vérification Clé API (.env)
    if os.path.exists(ENV_FILE):
        print("Environment file detected.")
        with open(ENV_FILE, "r") as f:
            content = f.read()
            if API_KEY_VARIABLE in content:
                print("API key present (format not verified).")
            else:
                print("No API key variable found in environment file.")
                all_good = False
    else:
        print("Environment file missing (copy .env.example).")
        all_good = False

    # 3. Vérification Logs
    try:
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
            print("Logs directory created.")
    except OSError as e:
        print(f"An OS error occurred: {e}")
        all_good = False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        all_good = False

    if all_good:
        print("\nAll set! You can start.")
    else:
        print("\nFix the errors before continuing.")

if __name__ == "__main__":
    check_environment()
