# tests/test_validation_agent.py
import pytest
import ast
import os
from tools.run_tests import run_tests
from agents.test_validation_agent import (
    validation_node,
    generate_report
)


# ── Tool Tests (Rule-Based) ──────────────────────────────

class TestRunTestsTool:

    def test_passing_tests_counted(self):
        """Tool must correctly count passing tests."""
        test_code = (
            "def test_add():\n"
            "    assert 1 + 1 == 2\n\n"
            "def test_sub():\n"
            "    assert 5 - 3 == 2\n"
        )
        result = run_tests(test_code, "x = 1\n")
        assert result["passed"] >= 2
        assert result["failed"] == 0

    def test_failing_tests_counted(self):
        """Tool must correctly count failing tests."""
        test_code = (
            "def test_always_fails():\n"
            "    assert 1 == 2\n"
        )
        result = run_tests(test_code, "x = 1\n")
        assert result["failed"] >= 1

    def test_returns_required_keys(self):
        """Output must contain passed, failed, errors."""
        result = run_tests(
            "def test_x(): pass\n", "x = 1\n"
        )
        assert "passed" in result
        assert "failed" in result
        assert "errors" in result

    def test_errors_is_list(self):
        """Errors field must always be a list."""
        result = run_tests(
            "def test_x(): pass\n", "x = 1\n"
        )
        assert isinstance(result["errors"], list)

    def test_raises_on_empty_test_code(self):
        """Must raise ValueError for empty test code."""
        with pytest.raises(ValueError):
            run_tests("", "x = 1\n")

    def test_raises_on_empty_fixed_code(self):
        """Must raise ValueError for empty fixed code."""
        with pytest.raises(ValueError):
            run_tests("def test_x(): pass\n", "")


# ── Agent Tests ───────────────────────────────────────────

class TestValidationAgent:

    def test_generates_valid_python_tests(
            self, base_state):
        """Generated test code must be valid Python."""
        base_state["fixed_code"] = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        base_state["code_summary"] = (
            "Module with an add function."
        )
        result = validation_node(base_state)
        try:
            ast.parse(result["test_code"])
            valid = True
        except SyntaxError:
            valid = False
        assert valid

    def test_test_results_populated(self, base_state):
        """test_results must be populated after agent runs."""
        base_state["fixed_code"] = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        base_state["code_summary"] = "Adds two numbers."
        result = validation_node(base_state)
        assert "passed" in result["test_results"]
        assert "failed" in result["test_results"]
        assert "errors" in result["test_results"]

    def test_final_report_created(self, base_state):
        """Final report file must be created on disk."""
        base_state["fixed_code"] = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        base_state["code_summary"] = "Adds two numbers."
        result = validation_node(base_state)
        assert os.path.exists(result["final_report_path"])

    def test_status_completed_on_success(
            self, base_state):
        """Status must be completed after successful run."""
        base_state["fixed_code"] = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        base_state["code_summary"] = "Adds two numbers."
        result = validation_node(base_state)
        assert result["status"] == "completed"

    def test_test_code_not_empty(self, base_state):
        """Generated test code must not be empty."""
        base_state["fixed_code"] = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        base_state["code_summary"] = "Adds two numbers."
        result = validation_node(base_state)
        assert result["test_code"].strip() != ""

    def test_logs_populated(self, base_state):
        """Logs must be populated after agent runs."""
        base_state["fixed_code"] = (
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
        )
        base_state["code_summary"] = "Adds two numbers."
        result = validation_node(base_state)
        assert len(result["logs"]) > 0