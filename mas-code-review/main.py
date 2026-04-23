# main.py
import os
import sys
from graph.pipeline import build_pipeline
from state.agent_state import AgentState


def main():
    """
    CLI entry point for the MAS Code Review Pipeline.
    Accepts a Python file path and runs all 4 agents.
    """
    print("=" * 50)
    print("   MAS Code Review Pipeline")
    print("   Powered by LangGraph + llama3:8b")
    print("=" * 50)

    # Get file path from argument or prompt
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input(
            "\nEnter path to Python file: "
        ).strip()

    # Validate file exists
    if not os.path.exists(file_path):
        print(f"\n❌ File not found: {file_path}")
        sys.exit(1)

    if not file_path.endswith(".py"):
        print("\n❌ Only .py files are supported.")
        sys.exit(1)

    print(f"\n📂 Analyzing: {file_path}")
    print("🚀 Starting pipeline...\n")

    # Initialize global state
    initial_state: AgentState = {
        "file_path": file_path,
        "raw_code": "",
        "code_summary": "",
        "functions": [],
        "imports": [],
        "complexity_score": 0,
        "bug_report": [],
        "lint_output": "",
        "security_issues": [],
        "fixed_code": "",
        "fix_summary": [],
        "test_code": "",
        "test_results": {},
        "final_report_path": "",
        "logs": [],
        "status": "running"
    }

    try:
        pipeline = build_pipeline()
        final_state = pipeline.invoke(initial_state)

        print("\n" + "=" * 50)
        print("   PIPELINE RESULTS")
        print("=" * 50)
        print(f"✅ Status        : {final_state['status']}")
        print(f"📝 Functions     : {final_state['functions']}")
        print(f"🔢 Complexity    : {final_state['complexity_score']}")
        print(f"🐛 Bugs Found    : {len(final_state['bug_report'])}")
        print(f"🔐 Security Issues: {len(final_state['security_issues'])}")
        print(f"✨ Fixes Applied : {len(final_state['fix_summary'])}")
        print(f"🧪 Tests Passed  : {final_state['test_results'].get('passed', 0)}")
        print(f"❌ Tests Failed  : {final_state['test_results'].get('failed', 0)}")
        print(f"📄 Report Saved  : {final_state['final_report_path']}")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()