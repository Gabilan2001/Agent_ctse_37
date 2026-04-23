# test_agent4.py
from agents.test_validation_agent import test_validation_node

state = {
    "file_path": "tests/sample_inputs/clean_code.py",
    "raw_code": "def hello():\n    return 'hello'\n",
    "code_summary": (
        "A simple module with a hello function "
        "that returns a greeting string."
    ),
    "functions": ["hello"],
    "imports": [],
    "complexity_score": 0,
    "bug_report": [
        {
            "line": 1,
            "type": "style",
            "severity": "LOW",
            "description": "trailing whitespace"
        }
    ],
    "lint_output": "W291 trailing whitespace",
    "security_issues": [],
    "fixed_code": (
        "def hello():\n"
        "    # FIX: Remove trailing whitespace\n"
        "    return 'hello'\n"
    ),
    "fix_summary": ["# FIX: Remove trailing whitespace"],
    "test_code": "",
    "test_results": {},
    "final_report_path": "",
    "logs": [
        "CodeUnderstandingAgent: done",
        "BugAnalystAgent: 1 issue found",
        "FixGenerationAgent: 1 fix applied"
    ],
    "status": "running"
}

result = test_validation_node(state)
print("Test Results:", result["test_results"])
print("Report saved to:", result["final_report_path"])
print("Status:", result["status"])