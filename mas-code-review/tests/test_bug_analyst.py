# tests/test_bug_analyst.py
import pytest
from tools.run_linter_and_scanner import run_linter_and_scanner
from agents.bug_analyst_agent import bug_analyst_node, parse_bug_report


# ── Tool Tests (Rule-Based) ──────────────────────────────

class TestLinterAndScannerTool:

    def test_detects_unused_import(self, tmp_path):
        """Flake8 must detect unused imports."""
        code = "import os\nx = 1\n"
        f = tmp_path / "test.py"
        f.write_text(code)
        result = run_linter_and_scanner(str(f))
        assert "F401" in result["lint_output"]

    def test_detects_hardcoded_password(self, tmp_path):
        """Bandit must flag hardcoded credentials."""
        code = 'password = "admin123"\n'
        f = tmp_path / "vuln.py"
        f.write_text(code)
        result = run_linter_and_scanner(str(f))
        assert len(result["security_issues"]) > 0

    def test_clean_code_no_security_issues(self, tmp_path):
        """Clean code must return no security issues."""
        code = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        f = tmp_path / "clean.py"
        f.write_text(code)
        result = run_linter_and_scanner(str(f))
        assert result["security_issues"] == []

    def test_returns_correct_keys(self, tmp_path):
        """Tool output must always have required keys."""
        f = tmp_path / "t.py"
        f.write_text("x = 1\n")
        result = run_linter_and_scanner(str(f))
        assert "lint_output" in result
        assert "security_issues" in result

    def test_security_issues_is_list(self, tmp_path):
        """Security issues must always be a list."""
        f = tmp_path / "t.py"
        f.write_text("x = 1\n")
        result = run_linter_and_scanner(str(f))
        assert isinstance(result["security_issues"], list)

    def test_raises_on_missing_file(self):
        """Must raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            run_linter_and_scanner("nonexistent.py")


# ── Agent Tests ───────────────────────────────────────────

class TestBugAnalystAgent:

    def test_bug_report_not_empty_for_buggy_code(
            self, base_state, sample_buggy_code):
        """Agent must find bugs in known buggy code."""
        base_state["file_path"] = sample_buggy_code
        with open(sample_buggy_code) as f:
            base_state["raw_code"] = f.read()
        base_state["code_summary"] = "A login module."
        result = bug_analyst_node(base_state)
        assert len(result["bug_report"]) > 0

    def test_bug_report_has_required_fields(
            self, base_state, sample_buggy_code):
        """Each bug must have line, type, severity, description."""
        base_state["file_path"] = sample_buggy_code
        with open(sample_buggy_code) as f:
            base_state["raw_code"] = f.read()
        base_state["code_summary"] = "A login module."
        result = bug_analyst_node(base_state)
        for bug in result["bug_report"]:
            assert "line" in bug
            assert "type" in bug
            assert "severity" in bug
            assert "description" in bug

    def test_severity_values_are_valid(
            self, base_state, sample_buggy_code):
        """Severity must be LOW, MEDIUM, HIGH, or CRITICAL."""
        base_state["file_path"] = sample_buggy_code
        with open(sample_buggy_code) as f:
            base_state["raw_code"] = f.read()
        base_state["code_summary"] = "A login module."
        result = bug_analyst_node(base_state)
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        for bug in result["bug_report"]:
            assert bug["severity"] in valid

    def test_state_keys_populated(
            self, base_state, sample_buggy_code):
        """lint_output and security_issues must be populated."""
        base_state["file_path"] = sample_buggy_code
        with open(sample_buggy_code) as f:
            base_state["raw_code"] = f.read()
        base_state["code_summary"] = "A login module."
        result = bug_analyst_node(base_state)
        assert result["lint_output"] != ""
        assert isinstance(result["security_issues"], list)

    def test_parse_bug_report_valid_json(self):
        """parse_bug_report must handle valid JSON."""
        content = '[{"line":1,"type":"bug","severity":"HIGH","description":"test"}]'
        result = parse_bug_report(content)
        assert len(result) == 1
        assert result[0]["severity"] == "HIGH"

    def test_parse_bug_report_handles_invalid(self):
        """parse_bug_report must handle invalid JSON gracefully."""
        result = parse_bug_report("not valid json at all")
        assert isinstance(result, list)
        assert len(result) > 0