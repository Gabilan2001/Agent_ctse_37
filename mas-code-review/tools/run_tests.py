# tools/run_tests.py
import subprocess
import tempfile
import os
from typing import TypedDict, List


class TestResult(TypedDict):
    passed: int
    failed: int
    errors: List[str]


def run_tests(
    test_code: str,
    fixed_code: str
) -> TestResult:
    """
    Saves generated test code and fixed code to temporary
    files, then executes pytest via subprocess to validate
    the fixed implementation.

    Args:
        test_code (str): Generated pytest test file content.
        fixed_code (str): The fixed Python source code
                          being tested.

    Returns:
        TestResult: Contains passed (int), failed (int),
                    and errors (List[str]).

    Raises:
        ValueError: If test_code or fixed_code is empty.
        RuntimeError: If pytest is not installed.
    """
    if not test_code or not test_code.strip():
        raise ValueError("Test code cannot be empty.")

    if not fixed_code or not fixed_code.strip():
        raise ValueError("Fixed code cannot be empty.")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save fixed code as solution.py
        code_path = os.path.join(tmpdir, "solution.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # Save test file as test_solution.py
        test_path = os.path.join(tmpdir, "test_solution.py")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        # Run pytest with verbose output
        result = subprocess.run(
            ["pytest", test_path, "-v", "--tb=short",
             "--no-header"],
            capture_output=True,
            text=True,
            cwd=tmpdir
        )

    output = result.stdout + result.stderr

    # Count passed and failed
    # Count passed and failed
    passed = output.count("PASSED")
    failed = output.count("FAILED")
    
    # Also try to get from summary line e.g. "1 passed, 0 failed"
    import re
    summary = re.search(
        r"(\d+) passed", output
    )
    if summary:
        passed = int(summary.group(1))
    summary_fail = re.search(
        r"(\d+) failed", output
    )
    if summary_fail:
        failed = int(summary_fail.group(1))
        
    errors = [
        line.strip()
        for line in output.split("\n")
        if "FAILED" in line or "ERROR" in line
    ]

    return {
        "passed": passed,
        "failed": failed,
        "errors": errors
    }