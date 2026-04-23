# test_agent2.py
from agents.bug_analyst_agent import bug_analyst_node

state = {
    "file_path": "tests/sample_inputs/clean_code.py",
    "raw_code": "def hello(): \n    return 'hello' \n",
    "code_summary": "A simple module with a hello function.",
    "functions": ["hello"],
    "imports": [], "complexity_score": 0,
    "bug_report": [], "lint_output": "",
    "security_issues": [], "fixed_code": "",
    "fix_summary": [], "test_code": "",
    "test_results": {}, "final_report_path": "",
    "logs": [], "status": "running"
}

result = bug_analyst_node(state)
print("Bugs found:", len(result["bug_report"]))
print("Bug report:", result["bug_report"])
print("Lint output:", result["lint_output"])
print("Status:", result["status"])