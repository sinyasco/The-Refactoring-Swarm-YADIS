"""
Refactoring Swarm Orchestrator
Multi-agent system for automated code refactoring with self-healing capabilities.

Workflow per file:
  auditor → tester → fixer → judge
                       ↑           |
                       └── retry ──┘
"""
import argparse
import time
import sys
import os
from dataclasses import dataclass
from typing import TypedDict, Literal
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from src.utils.logger import log_experiment, ActionType
from src.auditor import Auditor
from src.tester import Tester          # ← NEW
from src.fixer import Fixer
from src.judge import Judge

# Load environment variables FIRST
load_dotenv()

# Constants
MAX_ITER = 10                  # Maximum iterations (stops early if successful)
RECURSION_LIMIT_BUFFER = 100   # Buffer for recursion limit


@dataclass
class Config:
    """Configuration for the refactoring system."""
    target_dir: str
    groq_key: str


class AgentState(TypedDict):
    """State passed between agents in the workflow."""
    file_path: str
    plan: dict | None
    test_file: str | None          # ← NEW: path of the generated test file
    iteration: int
    max_iter: int
    success: bool
    test_logs: str
    error: str | None


# ---------------------------------------------------------------------------
# Environment / file discovery helpers
# ---------------------------------------------------------------------------

def validate_environment() -> str:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("   Please create a .env file with: GROQ_API_KEY=your_key_here")
        print("   Get your free API key at: https://console.groq.com/keys")
        sys.exit(1)
    return groq_key


def discover_python_files(target_dir: str) -> list[str]:
    if not os.path.exists(target_dir):
        print(f"❌ Error: Directory '{target_dir}' does not exist")
        sys.exit(1)

    py_files = [
        os.path.join(target_dir, f)
        for f in os.listdir(target_dir)
        if f.endswith(".py") and not f.startswith("test_")   # skip test files themselves
    ]

    if not py_files:
        print(f"⚠️  Warning: No Python files found in '{target_dir}'")

    return py_files


# ---------------------------------------------------------------------------
# Agent node factories
# ---------------------------------------------------------------------------

def create_auditor_node(config: Config):
    auditor = Auditor()

    def auditor_node(state: AgentState) -> AgentState:
        print(f"\n  🔍 Auditor analyzing (iteration {state['iteration']}/{state['max_iter']})...")
        time.sleep(2)
        try:
            plan = auditor.analyze(state["file_path"], groq_key=config.groq_key)
            log_experiment(
                "Auditor", "Groq", ActionType.ANALYSIS,
                {"input_prompt": f"Analyze {state['file_path']}", "output_response": str(plan)},
                "SUCCESS",
            )
            return {**state, "plan": plan, "error": None}
        except Exception as e:
            error_msg = f"Auditor failed: {e}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Auditor", "Groq", ActionType.ANALYSIS,
                {"input_prompt": f"Analyze {state['file_path']}", "output_response": error_msg},
                "FAILURE",
            )
            return {**state, "plan": None, "error": error_msg, "success": False}

    return auditor_node


def create_tester_node(config: Config):
    """
    Tester agent — generates (or regenerates) a test file for the target source.
    On the first iteration it creates the test file.
    On retries it regenerates it so it stays aligned with any audit-plan updates.
    """
    tester = Tester(config.groq_key)

    def tester_node(state: AgentState) -> AgentState:
        if state.get("error") or not state.get("plan"):
            print("  ⏭️  Tester skipped (previous error or no plan)")
            return state

        print(f"  🧪 Tester generating tests (iteration {state['iteration']}/{state['max_iter']})...")
        time.sleep(1)

        try:
            test_file = tester.generate_tests(state["file_path"], plan=state.get("plan"))
            log_experiment(
                "Tester", "Groq", ActionType.ANALYSIS,
                {"input_prompt": f"Generate tests for {state['file_path']}", "output_response": test_file},
                "SUCCESS",
            )
            return {**state, "test_file": test_file, "error": None}
        except Exception as e:
            error_msg = f"Tester failed: {e}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Tester", "Groq", ActionType.ANALYSIS,
                {"input_prompt": f"Generate tests", "output_response": error_msg},
                "FAILURE",
            )
            # Non-fatal: continue even without a test file (Judge will fall back to syntax check)
            return {**state, "test_file": None, "error": None}

    return tester_node


def create_fixer_node(config: Config):
    fixer = Fixer(config.groq_key)

    def fixer_node(state: AgentState) -> AgentState:
        if state.get("error") or not state.get("plan"):
            print("  ⏭️  Fixer skipped (previous error)")
            return state

        print("  🔧 Fixer applying changes...")
        time.sleep(2)

        try:
            fixer.apply_fix(state["plan"])
            log_experiment(
                "Fixer", "Groq", ActionType.FIX,
                {"input_prompt": f"Apply plan to {state['plan']['file']}", "output_response": str(state["plan"])},
                "SUCCESS",
            )
            return {**state, "error": None}
        except Exception as e:
            error_msg = f"Fixer failed: {e}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Fixer", "Groq", ActionType.FIX,
                {"input_prompt": "Apply fix", "output_response": error_msg},
                "FAILURE",
            )
            return {**state, "error": error_msg, "success": False}

    return fixer_node


def create_judge_node(config: Config):
    judge = Judge(config.groq_key)

    def judge_node(state: AgentState) -> AgentState:
        if state.get("error"):
            print("  ⏭️  Judge skipped (previous error)")
            return state

        print("  ⚖️  Judge running tests...")

        try:
            success, test_logs = judge.run_tests(state["file_path"])

            if success:
                print("  ✅ Tests PASSED!")
            else:
                print("  ❌ Tests FAILED")
                print(f"     Preview: {test_logs[:200]}...")

            log_experiment(
                "Judge", "None", ActionType.DEBUG,
                {"input_prompt": f"Run tests on {state['file_path']}", "output_response": test_logs},
                "SUCCESS" if success else "FAILURE",
            )
            return {
                **state,
                "success": success,
                "test_logs": test_logs,
                "error": None if success else "Tests failed",
            }
        except Exception as e:
            error_msg = f"Judge failed: {e}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Judge", "None", ActionType.DEBUG,
                {"input_prompt": "Run tests", "output_response": error_msg},
                "FAILURE",
            )
            return {**state, "success": False, "test_logs": error_msg, "error": error_msg}

    return judge_node


# ---------------------------------------------------------------------------
# Control-flow helpers
# ---------------------------------------------------------------------------

def should_retry(state: AgentState) -> Literal["retry", "end"]:
    if state.get("success", False):
        return "end"

    if state["iteration"] >= state["max_iter"]:
        print(f"\n  ⛔ Stopping: Max iterations ({state['max_iter']}) reached")
        return "end"

    error = state.get("error", "")
    if error and error != "Tests failed":
        print("\n  ⛔ Stopping: Fatal error detected")
        return "end"

    print("\n  🔄 Retrying...")
    return "retry"


def increment_iteration(state: AgentState) -> AgentState:
    return {**state, "iteration": state["iteration"] + 1, "error": None}


# ---------------------------------------------------------------------------
# Workflow construction
# ---------------------------------------------------------------------------

def build_workflow(config: Config) -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("auditor", create_auditor_node(config))
    workflow.add_node("tester",  create_tester_node(config))   # ← NEW
    workflow.add_node("fixer",   create_fixer_node(config))
    workflow.add_node("judge",   create_judge_node(config))
    workflow.add_node("increment", increment_iteration)

    workflow.set_entry_point("auditor")
    workflow.add_edge("auditor", "tester")    # ← auditor → tester
    workflow.add_edge("tester",  "fixer")     # ← tester  → fixer
    workflow.add_edge("fixer",   "judge")

    workflow.add_conditional_edges(
        "judge",
        should_retry,
        {"retry": "increment", "end": END},
    )
    # On retry: re-run auditor (which re-plans) then tester (which regenerates tests)
    workflow.add_edge("increment", "auditor")

    return workflow.compile()


# ---------------------------------------------------------------------------
# File processing & CLI
# ---------------------------------------------------------------------------

def process_file(workflow: StateGraph, file_path: str, max_iter: int) -> bool:
    print(f"\n{'='*60}")
    print(f"📄 Processing: {file_path}")
    print(f"{'='*60}")

    initial_state: AgentState = {
        "file_path": file_path,
        "plan": None,
        "test_file": None,
        "iteration": 1,
        "max_iter": max_iter,
        "success": False,
        "test_logs": "",
        "error": None,
    }

    try:
        # Each iteration: auditor → tester → fixer → judge → increment = 5 nodes
        recursion_limit = (max_iter * 5) + RECURSION_LIMIT_BUFFER
        print(f"  ℹ️  Recursion limit set to: {recursion_limit}")

        final_state = workflow.invoke(
            initial_state,
            config={"recursion_limit": recursion_limit},
        )

        if final_state["success"]:
            print(f"\n✅ SUCCESS: {file_path} passed all tests!")
            return True
        else:
            print(f"\n⚠️  INCOMPLETE: {file_path} did not pass after {max_iter} iterations")
            if final_state.get("test_logs"):
                print("\n📋 Final test output:")
                print(final_state["test_logs"][:500])
                if len(final_state["test_logs"]) > 500:
                    print("... (truncated)")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: Failed to process {file_path}\n   Error: {e}")
        log_experiment(
            "System", "None", ActionType.DEBUG,
            {"input_prompt": f"Process {file_path}", "output_response": str(e)},
            "FAILURE",
        )
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run the Refactoring Swarm — Multi-agent code refactoring system"
    )
    parser.add_argument("--target_dir", type=str, required=True,
                        help="Directory containing Python files to refactor")
    parser.add_argument("--max_iter", type=int, default=MAX_ITER,
                        help=f"Maximum iterations per file (default: {MAX_ITER})")
    args = parser.parse_args()

    groq_key = validate_environment()
    config = Config(target_dir=args.target_dir, groq_key=groq_key)

    log_experiment(
        "System", "None", ActionType.DEBUG,
        {"input_prompt": "Startup", "output_response": f"Target: {config.target_dir}"},
        "SUCCESS",
    )

    print(f"\n{'='*60}")
    print("🚀 REFACTORING SWARM STARTED")
    print(f"{'='*60}")
    print(f"   Target directory : {config.target_dir}")
    print(f"   Max iterations   : {args.max_iter}")
    print(f"   AI Provider      : Groq API (Ultra-fast)")
    print(f"   Pipeline         : Auditor → Tester → Fixer → Judge")
    print(f"{'='*60}")

    py_files = discover_python_files(config.target_dir)
    print(f"\n   📂 Found {len(py_files)} Python file(s)")

    if not py_files:
        print("\n⚠️  No files to process. Exiting.")
        sys.exit(0)

    workflow = build_workflow(config)

    results = []
    for i, file_path in enumerate(py_files, 1):
        print(f"\n[File {i}/{len(py_files)}]")
        success = process_file(workflow, file_path, args.max_iter)
        results.append((file_path, success))

    # Summary
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")

    successful = sum(1 for _, ok in results if ok)
    total = len(results)

    for file_path, ok in results:
        print(f"  {'✅' if ok else '❌'} {os.path.basename(file_path)}")

    print(f"\n{'='*60}")
    rate = 100 * successful // total if total else 0
    print(f"  Success Rate: {successful}/{total} files ({rate}%)")
    print(f"{'='*60}")
    print(f"\n{'✅ MISSION COMPLETE' if successful == total else '⚠️  MISSION INCOMPLETE'}")

    sys.exit(0 if successful == total else 1)


if __name__ == "__main__":
    main()