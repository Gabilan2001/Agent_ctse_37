# state/agent_state.py
from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    # --- Input ---
    file_path: str
    raw_code: str

    # --- CodeUnderstandingAgent output ---
    code_summary: str
    functions: List[str]
    imports: List[str]
    complexity_score: int

    # --- BugAnalystAgent output ---
    bug_report: List[dict]
    lint_output: str
    security_issues: List[dict]

    # --- FixGenerationAgent output ---
    fixed_code: str
    fix_summary: List[str]

    # --- TestValidationAgent output ---
    test_code: str
    test_results: dict
    final_report_path: str

    # --- System-wide ---
    logs: List[str]
    status: str