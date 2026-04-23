# test_agent1.py
from agents.code_understanding_agent import code_understanding_node

state = {
    "file_path": "tests/sample_inputs/clean_code.py",
    "raw_code": "", "code_summary": "", "functions": [],
    "imports": [], "complexity_score": 0, "bug_report": [],
    "lint_output": "", "security_issues": [], "fixed_code": "",
    "fix_summary": [], "test_code": "", "test_results": {},
    "final_report_path": "", "logs": [], "status": "running"
}

result = code_understanding_node(state)
print("Summary:", result["code_summary"][:150])
print("Functions:", result["functions"])
print("Imports:", result["imports"])
print("Complexity:", result["complexity_score"])
print("Status:", result["status"])