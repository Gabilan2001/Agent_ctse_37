# test_agent3.py
from agents.fix_generation_agent import fix_generation_node

state = {
    "file_path": "tests/sample_inputs/clean_code.py",
    "raw_code": "def hello(): \n    return 'hello' \n",
    "code_summary": "A simple module with a hello function.",
    "functions": ["hello"],
    "imports": [], "complexity_score": 0,
    "bug_report": [
        {
            "line": 1,
            "type": "style",
            "severity": "LOW",
            "description": "trailing whitespace"
        }
    ],
    "lint_output": "W291 trailing whitespace",
    "security_issues": [], "fixed_code": "",
    "fix_summary": [], "test_code": "",
    "test_results": {}, "final_report_path": "",
    "logs": [], "status": "running"
}

result = fix_generation_node(state)
print("Fixed code:")
print(result["fixed_code"])
print("Fix summary:", result["fix_summary"])
print("Status:", result["status"])