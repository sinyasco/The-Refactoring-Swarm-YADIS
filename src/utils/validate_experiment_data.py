import json
import os
import sys
from src.utils.logger import ActionType  # <- on importe la vraie classe

LOG_FILE = os.path.join("logs", "experiment_data.json")

REQUIRED_FIELDS = [
    "id",
    "timestamp",
    "agent",
    "model",
    "action",
    "details",
    "status"
]

REQUIRED_DETAIL_FIELDS = [
    "input_prompt",
    "output_response"
]

# Noms d'agents autorisés
VALID_AGENTS = ["Auditor_Agent", "Fixer_Agent", "Judge_Agent"]

def fail(message: str):
    print(f"❌ Validation Error: {message}")
    sys.exit(1)

def validate():
    if not os.path.exists(LOG_FILE):
        fail("experiment_data.json file does not exist.")

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            fail("experiment_data.json is not valid JSON.")

    if not isinstance(data, list) or len(data) == 0:
        fail("experiment_data.json must be a non-empty list.")

    valid_actions = [a.value for a in ActionType]  # <- toutes les valeurs de l'enum

    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            fail(f"Entry #{index} is not a JSON object.")

        for field in REQUIRED_FIELDS:
            if field not in entry:
                fail(f"Missing field '{field}' in entry #{index}.")

        if entry["agent"] not in VALID_AGENTS:
            fail(f"Invalid agent_name '{entry['agent']}' in entry #{index}.")

        if entry["action"] not in valid_actions:
            fail(f"Invalid action '{entry['action']}' in entry #{index}.")

        if not isinstance(entry["details"], dict):
            fail(f"'details' must be an object in entry #{index}.")

        for detail_field in REQUIRED_DETAIL_FIELDS:
            if detail_field not in entry["details"]:
                fail(f"Missing '{detail_field}' in details of entry #{index}.")

    print("✅ experiment_data.json validation SUCCESS.")
    sys.exit(0)

if __name__ == "__main__":
    validate()
