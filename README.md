# 🐝 The Refactoring Swarm

> An autonomous multi-agent LLM system that audits, repairs, and validates messy Python code — no human intervention required.

![Python](https://img.shields.io/badge/Python-3.10%2F3.11-blue?logo=python)
![Groq](https://img.shields.io/badge/Powered%20by-Groq-F55036?logo=groq)
![ESI](https://img.shields.io/badge/ESI-IGL%20Lab%202025--2026-green)

---

## 📖 Overview

**The Refactoring Swarm** is a multi-agent AI system built for the IGL Lab practical session at the National School of Computer Science (ESI), Academic Year 2025-2026.

The system takes a folder of **buggy, undocumented, and untested Python code** as input and delivers a **clean, functional, test-passing version** as output — autonomously, through the collaboration of specialized AI agents.

This project is also part of an **Empirical Software Engineering research experiment** studying LLM-assisted software maintenance.

---

## 🏗️ Architecture
```
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
```

---

## 👥 Team Roles

| Role | Responsibility |
|------|---------------|
| 🧠 **Orchestrator** | Designs the execution graph, manages `main.py` and agent relay logic |
| 🛠️ **Toolsmith** | Builds internal tools (file I/O, pylint, pytest), enforces sandbox security |
| 💬 **Prompt Engineer** | Writes and versions system prompts, optimizes for token efficiency |
| 📊 **Data Officer** | Owns telemetry — ensures all agent actions are logged to `experiment_data.json` |

---

## 📁 Project Structure
```
/refactoring-swarm
│
├── main.py                   🔒 Entry point (CLI: --target_dir)
├── requirements.txt          🔒 Dependencies
├── .env                      🔒 API keys (never committed)
├── check_setup.py            🔒 Environment verification script
│
├── /src                      👈 Agent and tool source code
│   └── /utils
│       └── logger.py             Telemetry & logging module
│
├── /logs                     🔒 Auto-generated output
│   └── experiment_data.json      Full interaction history
│
└── /sandbox                  👈 Working directory for code repair
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python **3.10** or **3.11** ⚠️ (3.12+ not supported)
- Git
- A free GROQ API KEY https://console.groq.com

### 1. Clone the repo
```bash
git clone https://github.com/sinyasco/The-Refactoring-Swarm-YADIS.git
cd The-Refactoring-Swarm-YADIS
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
GROQ_API_KEY="your key"
```

> ⚠️ Never commit your `.env` file.

### 5. Verify your setup
```bash
python check_setup.py
```

All checks must show ✅ before you start coding.

---

## 🚀 Usage
```bash
python main.py --target_dir "./sandbox/your_buggy_code_folder"
```


## 🔬 Research Context

This project contributes to an empirical study on LLM-assisted software engineering. Interaction logs are anonymized and used to analyze how developers collaborate with AI systems during software maintenance tasks.

---

