"""
Refactoring Swarm Orchestrator
Multi-agent system for automated code refactoring with self-healing capabilities.
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
from src.fixer import Fixer
from src.judge import Judge

# Load environment variables FIRST
load_dotenv()

# Constants
MAX_ITER = 10  # Maximum iterations as specified (stops early if successful)

@dataclass
class Config:
    """Configuration for the refactoring system."""
    target_dir: str
    groq_key: str


class AgentState(TypedDict):
    """State passed between agents in the workflow."""
    file_path: str
    plan: dict | None
    iteration: int
    max_iter: int
    success: bool
    test_logs: str
    error: str | None


def validate_environment() -> str:
    """Validate that required environment variables are set."""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("   Please create a .env file with: GROQ_API_KEY=your_key_here")
        print("   Get your free API key at: https://console.groq.com/keys")
        sys.exit(1)
    return groq_key


def discover_python_files(target_dir: str) -> list[str]:
    """Find all Python files in the target directory."""
    if not os.path.exists(target_dir):
        print(f"❌ Error: Directory '{target_dir}' does not exist")
        sys.exit(1)
    
    py_files = [
        os.path.join(target_dir, f) 
        for f in os.listdir(target_dir) 
        if f.endswith(".py")
    ]
    
    if not py_files:
        print(f"⚠️  Warning: No Python files found in '{target_dir}'")
    
    return py_files


def create_auditor_node(config: Config):
    """Create the Auditor agent node."""
    auditor = Auditor()
    
    def auditor_node(state: AgentState) -> AgentState:
        """Analyze the file and create a refactoring plan."""
        print(f"\n  🔍 Auditor analyzing (iteration {state['iteration']}/{state['max_iter']})...")
        time.sleep(2)

        try:
            plan = auditor.analyze(state["file_path"], groq_key=config.groq_key)
            
            log_experiment(
                "Auditor", "Groq", ActionType.ANALYSIS,
                {"input_prompt": f"Analyze {state['file_path']}", "output_response": str(plan)},
                "SUCCESS"
            )
            
            return {
                **state,
                "plan": plan,
                "error": None
            }
        except Exception as e:
            error_msg = f"Auditor failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Auditor", "Groq", ActionType.ANALYSIS,
                {"input_prompt": f"Analyze {state['file_path']}", "output_response": error_msg},
                "FAILURE"
            )
            return {
                **state,
                "plan": None,
                "error": error_msg,
                "success": False
            }
    
    return auditor_node


def create_fixer_node(config: Config):
    """Create the Fixer agent node."""
    fixer = Fixer(config.groq_key)
    
    def fixer_node(state: AgentState) -> AgentState:
        """Apply the refactoring plan to the file."""
        if state.get("error") or not state.get("plan"):
            print(f"  ⏭️  Fixer skipped (previous error)")
            return state
        
        print(f"  🔧 Fixer applying changes...")
        time.sleep(2)

        try:
            fixer.apply_fix(state["plan"])
            
            log_experiment(
                "Fixer", "Groq", ActionType.FIX,
                {"input_prompt": f"Apply plan to {state['plan']['file']}", "output_response": str(state['plan'])},
                "SUCCESS"
            )
            
            return {
                **state,
                "error": None
            }
        except Exception as e:
            error_msg = f"Fixer failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Fixer", "Groq", ActionType.FIX,
                {"input_prompt": f"Apply fix", "output_response": error_msg},
                "FAILURE"
            )
            return {
                **state,
                "error": error_msg,
                "success": False
            }
    
    return fixer_node


def create_judge_node(config: Config):
    """Create the Judge agent node."""
    judge = Judge(config.groq_key)
    
    def judge_node(state: AgentState) -> AgentState:
        """Run tests and validate the refactored code."""
        if state.get("error"):
            print(f"  ⏭️  Judge skipped (previous error)")
            return state
        
        print(f"  ⚖️  Judge running tests...")

        try:
            success, test_logs = judge.run_tests(state["file_path"])
            
            if success:
                print(f"  ✅ Tests PASSED!")
            else:
                print(f"  ❌ Tests FAILED")
                # Show a preview of the error
                print(f"     Preview: {test_logs[:200]}...")
            
            log_experiment(
                "Judge", "None", ActionType.DEBUG,
                {"input_prompt": f"Run tests on {state['file_path']}", "output_response": test_logs},
                "SUCCESS" if success else "FAILURE"
            )
            
            return {
                **state,
                "success": success,
                "test_logs": test_logs,
                "error": None if success else "Tests failed"
            }
        except Exception as e:
            error_msg = f"Judge failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            log_experiment(
                "Judge", "None", ActionType.DEBUG,
                {"input_prompt": f"Run tests", "output_response": error_msg},
                "FAILURE"
            )
            return {
                **state,
                "success": False,
                "test_logs": error_msg,
                "error": error_msg
            }
    
    return judge_node


def should_retry(state: AgentState) -> Literal["retry", "end"]:
    """Determine if the workflow should retry or end."""
    # Success - we're done!
    if state.get("success", False):
        return "end"
    
    # Hit max iterations - stop
    if state["iteration"] >= state["max_iter"]:
        print(f"\n  ⛔ Stopping: Max iterations ({state['max_iter']}) reached")
        return "end"
    
    # Fatal error (not just test failure) - stop
    error = state.get("error", "")
    if error and error != "Tests failed":
        print(f"\n  ⛔ Stopping: Fatal error detected")
        return "end"
    
    # Otherwise, retry
    print(f"\n  🔄 Retrying...")
    return "retry"


def increment_iteration(state: AgentState) -> AgentState:
    """Increment the iteration counter for retry."""
    new_iteration = state["iteration"] + 1
    return {
        **state,
        "iteration": new_iteration,
        "error": None  # Clear error to allow retry
    }


def build_workflow(config: Config) -> StateGraph:
    """Construct the multi-agent workflow graph."""
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("auditor", create_auditor_node(config))
    workflow.add_node("fixer", create_fixer_node(config))
    workflow.add_node("judge", create_judge_node(config))
    workflow.add_node("increment", increment_iteration)
    
    # Define workflow edges
    workflow.set_entry_point("auditor")
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    
    # Conditional edge: retry or end
    workflow.add_conditional_edges(
        "judge",
        should_retry,
        {
            "retry": "increment",
            "end": END
        }
    )
    workflow.add_edge("increment", "auditor")
    
    return workflow.compile()


def process_file(workflow: StateGraph, file_path: str, max_iter: int) -> bool:
    """Process a single file through the refactoring workflow."""
    print(f"\n{'='*60}")
    print(f"📄 Processing: {file_path}")
    print(f"{'='*60}")
    
    initial_state: AgentState = {
        "file_path": file_path,
        "plan": None,
        "iteration": 1,
        "max_iter": max_iter,
        "success": False,
        "test_logs": "",
        "error": None
    }
    
    try:
        # Set recursion limit high enough for the workflow
        # Formula: (max_iter * nodes_per_iteration) + buffer
        # Each iteration: auditor -> fixer -> judge -> increment = 4 nodes
        recursion_limit = 100
        
        print(f"  ℹ️  Recursion limit set to: {recursion_limit}")
        
        final_state = workflow.invoke(
            initial_state,
            config={"recursion_limit": recursion_limit}
        )
        
        if final_state["success"]:
            print(f"\n✅ SUCCESS: {file_path} passed all tests!")
            return True
        else:
            print(f"\n⚠️  INCOMPLETE: {file_path} did not pass tests after {max_iter} iterations")
            if final_state.get("test_logs"):
                print(f"\n📋 Final test output:")
                print(final_state['test_logs'][:500])
                if len(final_state['test_logs']) > 500:
                    print("... (truncated)")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Failed to process {file_path}")
        print(f"   Error: {str(e)}")
        log_experiment(
            "System", "None", ActionType.DEBUG,
            {"input_prompt": f"Process {file_path}", "output_response": str(e)},
            "FAILURE"
        )
        return False


def main():
    """Main entry point for the refactoring orchestrator."""
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Run the Refactoring Swarm - Multi-agent code refactoring system"
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Directory containing Python files to refactor"
    )
    parser.add_argument(
        "--max_iter",
        type=int,
        default=MAX_ITER,
        help=f"Maximum iterations per file (default: {MAX_ITER})"
    )
    args = parser.parse_args()
    
    # Validate environment and setup
    groq_key = validate_environment()
    config = Config(
        target_dir=args.target_dir,
        groq_key=groq_key
    )
    
    # Log system startup
    log_experiment(
        "System", "None", ActionType.DEBUG,
        {"input_prompt": "Startup", "output_response": f"Target: {config.target_dir}"},
        "SUCCESS"
    )
    
    print(f"\n{'='*60}")
    print(f"🚀 REFACTORING SWARM STARTED")
    print(f"{'='*60}")
    print(f"   Target directory: {config.target_dir}")
    print(f"   Max iterations per file: {args.max_iter}")
    print(f"   AI Provider: Groq API (Ultra-fast)")
    print(f"{'='*60}")
    
    # Discover files to process
    py_files = discover_python_files(config.target_dir)
    print(f"\n   📂 Found {len(py_files)} Python file(s)")
    
    if not py_files:
        print("\n⚠️  No files to process. Exiting.")
        sys.exit(0)
    
    # Build workflow graph
    workflow = build_workflow(config)
    
    # Process each file
    results = []
    for i, file_path in enumerate(py_files, 1):
        print(f"\n[File {i}/{len(py_files)}]")
        success = process_file(workflow, file_path, args.max_iter)
        results.append((file_path, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for file_path, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {os.path.basename(file_path)}")
    
    print(f"\n{'='*60}")
    print(f"  Success Rate: {successful}/{total} files ({100*successful//total if total > 0 else 0}%)")
    print(f"{'='*60}")
    print(f"\n{'✅ MISSION COMPLETE' if successful == total else '⚠️  MISSION INCOMPLETE'}")
    
    # Exit with appropriate code
    sys.exit(0 if successful == total else 1)


if __name__ == "__main__":
    main()
