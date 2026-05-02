# tests/test_fix_generation.py
import pytest
import ast
import os
from tools.save_fixed_code import save_fixed_code
from agents.fix_generation_agent import (
    fix_generation_node,
    extract_fix_comments
)


# ── Tool Tests (Rule-Based) ──────────────────────────────

class TestSaveFixedCodeTool:

    def test_saves_file_to_outputs(self):
        """Tool must create a file in outputs directory."""
        path = save_fixed_code("x = 1\n", "test.py")
        assert os.path.exists(path)
        os.remove(path)

    def test_output_contains_correct_code(self):
        """Saved file content must match input exactly."""
        code = "def foo(): return 42\n"
        path = save_fixed_code(code, "original.py")
        with open(path) as f:
            assert f.read() == code
        os.remove(path)

    def test_raises_on_empty_code(self):
        """Must raise ValueError for empty input."""
        with pytest.raises(ValueError):
            save_fixed_code("", "file.py")

    def test_raises_on_whitespace_only(self):
        """Must raise ValueError for whitespace-only code."""
        with pytest.raises(ValueError):
            save_fixed_code("   \n  ", "file.py")

    def test_filename_contains_original_name(self):
        """Output filename must reference original file."""
        path = save_fixed_code("x = 1\n", "mymodule.py")
        assert "mymodule" in path
        os.remove(path)

    def test_output_in_outputs_directory(self):
        """Fixed file must be saved in outputs/ directory."""
        path = save_fixed_code("x = 1\n", "test.py")
        assert path.startswith("outputs/") or \
               path.startswith("outputs\\")
        os.remove(path)


# ── Agent Tests ───────────────────────────────────────────

class TestFixGenerationAgent:

    def test_fixed_code_is_valid_python(
            self, base_state, sample_buggy_code):
        """Fixed code must be parseable as valid Python."""
        base_state["file_path"] = sample_buggy_code
        with open(sample_buggy_code) as f:
            base_state["raw_code"] = f.read()
        base_state["code_summary"] = "A login module."
        base_state["bug_report"] = [
            {"line": 5, "type": "bug",
             "severity": "HIGH",
             "description": "Division by zero risk"}
        ]
        result = fix_generation_node(base_state)
        try:
            ast.parse(result["fixed_code"])
            valid = True
        except SyntaxError:
            valid = False
        assert valid

    def test_fixed_code_not_empty(
            self, base_state, sample_buggy_code):
        """Fixed code must never be empty."""
        base_state["file_path"] = sample_buggy_code
        with open(sample_buggy_code) as f:
            base_state["raw_code"] = f.read()
        base_state["bug_report"] = [
            {"line": 1, "type": "style",
             "severity": "LOW",
             "description": "missing type hints"}
        ]
        result = fix_generation_node(base_state)
        assert result["fixed_code"].strip() != ""

    def test_fix_summary_is_list(
            self, base_state, sample_clean_code):
        """Fix summary must always be a list."""
        base_state["file_path"] = sample_clean_code
        with open(sample_clean_code) as f:
            base_state["raw_code"] = f.read()
        base_state["bug_report"] = []
        result = fix_generation_node(base_state)
        assert isinstance(result["fix_summary"], list)

    def test_extract_fix_comments(self):
        """Must extract all # FIX: comments correctly."""
        code = (
            "def foo():\n"
            "    x = 1  # FIX: removed unused variable\n"
            "    return x  # FIX: added return\n"
        )
        fixes = extract_fix_comments(code)
        assert len(fixes) == 2

    def test_extract_fix_comments_none_found(self):
        """Must return default message when no FIX comments."""
        code = "def foo():\n    return 1\n"
        fixes = extract_fix_comments(code)
        assert len(fixes) > 0
        assert isinstance(fixes[0], str)

    def test_status_not_failed_on_success(
            self, base_state, sample_clean_code):
        """Status must not be failed after successful run."""
        base_state["file_path"] = sample_clean_code
        with open(sample_clean_code) as f:
            base_state["raw_code"] = f.read()
        base_state["bug_report"] = []
        result = fix_generation_node(base_state)
        assert result["status"] != "failed"