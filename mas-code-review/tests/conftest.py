# tests/conftest.py
import pytest
import tempfile
import os


@pytest.fixture
def sample_clean_code(tmp_path):
    """Clean Python file with no bugs."""
    code = (
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "def subtract(a: int, b: int) -> int:\n"
        "    return a - b\n"
    )
    f = tmp_path / "clean.py"
    f.write_text(code)
    return str(f)


@pytest.fixture
def sample_buggy_code(tmp_path):
    """Buggy Python file with known issues."""
    code = (
        "import os\n"
        "password = 'admin123'\n\n"
        "def divide(a, b):\n"
        "    return a / b\n\n"
        "def login(user, pwd):\n"
        "    if user == 'admin' and pwd == password:\n"
        "        return True\n"
    )
    f = tmp_path / "buggy.py"
    f.write_text(code)
    return str(f)


@pytest.fixture
def base_state():
    """Base pipeline state for testing."""
    return {
        "file_path": "",
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