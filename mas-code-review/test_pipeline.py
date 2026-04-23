# test_pipeline.py
from graph.pipeline import build_pipeline
from state.agent_state import AgentState

initial_state: AgentState = {
    "file_path": "tests/sample_inputs/clean_code.py",
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

print("Building pipeline...")
pipeline = build_pipeline()

print("Running full pipeline...")
final_state = pipeline.invoke(initial_state)

print("\n========== PIPELINE COMPLETE ==========")
print("Status:", final_state["status"])
print("Functions:", final_state["functions"])
print("Bugs found:", len(final_state["bug_report"]))
print("Tests passed:", final_state["test_results"].get("passed", 0))
print("Tests failed:", final_state["test_results"].get("failed", 0))
print("Report saved to:", final_state["final_report_path"])