📖 Overview
The Refactoring Swarm is a multi-agent AI system built for the IGL Lab practical session at the National School of Computer Science (ESI), Academic Year 2025-2026.
The system takes a folder of buggy, undocumented, and untested Python code as input and delivers a clean, functional, test-passing version as output — autonomously, through the collaboration of specialized AI agents.
This project is also part of an Empirical Software Engineering research experiment studying LLM-assisted software maintenance. All agent interactions are logged and anonymized for scientific analysis.

🏗️ Architecture
The swarm orchestrates 3 specialized agents in a feedback loop:
📁 Input (buggy code)
        │
        ▼
┌───────────────┐
│  🔍 Auditor   │  ── Reads code, runs static analysis, produces refactoring plan
└───────┬───────┘
        │ plan
        ▼
┌───────────────┐
│  🔧 Fixer     │  ── Applies fixes file by file based on the plan
└───────┬───────┘
        │ fixed code
        ▼
┌───────────────┐
│  ⚖️ Judge     │  ── Runs unit tests (pytest)
└───────┬───────┘
        │
   ✅ Pass? ──► 📁 Output (clean code)
        │
   ❌ Fail? ──► back to 🔧 Fixer (Self-Healing Loop, max 10 iterations)

👥 Team Roles
RoleResponsibility🧠 Orchestrator (Lead Dev)Designs the execution graph (LangGraph/CrewAI/AutoGen), manages main.py and agent relay logic🛠️ ToolsmithBuilds internal Python tools (file I/O, pylint, pytest), enforces sandbox security💬 Prompt EngineerWrites and versions system prompts, optimizes for token efficiency and accuracy📊 Data OfficerOwns telemetry — ensures all agent actions are logged to experiment_data.json

📁 Project Structure
/refactoring-swarm
│
├── main.py               🔒 Entry point (CLI: --target_dir)
├── requirements.txt      🔒 Dependencies
├── .env                  🔒 API keys (never committed)
├── check_setup.py        🔒 Environment verification script
│
├── /src                  👈 Agent and tool source code
│   └── /utils
│       └── logger.py         Telemetry & logging module
│
├── /logs                 🔒 Auto-generated output
│   └── experiment_data.json  Full interaction history
│
└── /sandbox              👈 Working directory for code repair

⚙️ Setup & Installation
Prerequisites

Python 3.10 or 3.11 (⚠️ 3.12+ not supported)
Git
A free GROQ API key

1. Clone the template
bashgit clone https://github.com/sinyasco/The-Refactoring-Swarm-YADIS.git
cd The-Refactoring-Swarm-YADIS
2. Create a virtual environment
bash# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
bashpip install -r requirements.txt
4. Configure your API key
bash# Duplicate the example file
cp .env.example .env
Then edit .env and add your key:
GROQ_API_KEY="..."


5. Verify your setup
bashpython check_setup.py
All checks must show ✅ before you start coding. Fix any ❌ first.

🚀 Usage
bashpython main.py --target_dir "./sandbox/your_buggy_code_folder"
The system will autonomously audit, fix, and test all Python files in the target directory. Results are saved back to the sandbox and all interactions are logged to logs/experiment_data.json.
