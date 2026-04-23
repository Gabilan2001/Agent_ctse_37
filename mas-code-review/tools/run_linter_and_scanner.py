# tools/run_linter_and_scanner.py
import subprocess
import json
import os
from typing import TypedDict, List


class ScanResult(TypedDict):
    lint_output: str
    security_issues: List[dict]


def run_linter_and_scanner(file_path: str) -> ScanResult:
    """
    Runs flake8 (linting) and bandit (security scanning)
    on a Python source file via subprocess.

    Args:
        file_path (str): Path to the Python file to analyze.

    Returns:
        ScanResult: Contains lint_output (str) and
                    security_issues (List[dict]).

    Raises:
        FileNotFoundError: If the file path is invalid.
        RuntimeError: If linter tools are not installed.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # --- Run flake8 linter ---
    lint_result = subprocess.run(
        ["flake8", file_path, "--max-line-length=100"],
        capture_output=True,
        text=True
    )
    lint_output = lint_result.stdout.strip()
    if not lint_output:
        lint_output = "No linting issues found."

    # --- Run bandit security scanner ---
    security_issues = []
    try:
        bandit_result = subprocess.run(
            ["bandit", "-r", file_path, "-f", "json", "-q"],
            capture_output=True,
            text=True
        )
        if bandit_result.stdout.strip():
            bandit_data = json.loads(bandit_result.stdout)
            security_issues = [
                {
                    "line": r.get("line_number", 0),
                    "issue": r.get("issue_text", ""),
                    "severity": r.get("issue_severity", "LOW"),
                    "confidence": r.get("issue_confidence", "LOW"),
                    "recommendation": r.get("more_info", "")
                }
                for r in bandit_data.get("results", [])
            ]
    except (json.JSONDecodeError, Exception) as e:
        security_issues = []

    return {
        "lint_output": lint_output,
        "security_issues": security_issues
    }