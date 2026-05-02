# tests/test_code_understanding.py
import pytest
import ast
from tools.read_and_parse_code import read_and_parse_code
from agents.code_understanding_agent import code_understanding_node


# ── Tool Tests (Rule-Based) ──────────────────────────────

class TestReadAndParseCodeTool:

    def test_extracts_function_names(self, tmp_path):
        """Tool must correctly extract all function names."""
        code = "def foo(): pass\ndef bar(): pass\n"
        f = tmp_path / "test.py"
        f.write_text(code)
        result = read_and_parse_code(str(f))
        assert "foo" in result["functions"]
        assert "bar" in result["functions"]

    def test_extracts_imports(self, tmp_path):
        """Tool must detect all import statements."""
        code = "import os\nimport sys\ndef run(): pass\n"
        f = tmp_path / "test.py"
        f.write_text(code)
        result = read_and_parse_code(str(f))
        assert "os" in result["imports"]
        assert "sys" in result["imports"]

    def test_complexity_score_is_integer(self, tmp_path):
        """Complexity score must always be an integer."""
        code = "def foo():\n    if True:\n        pass\n"
        f = tmp_path / "test.py"
        f.write_text(code)
        result = read_and_parse_code(str(f))
        assert isinstance(result["complexity_score"], int)

    def test_complexity_increases_with_branches(self, tmp_path):
        """More branches must increase complexity score."""
        simple = "def foo(): pass\n"
        complex_code = (
            "def foo():\n"
            "    if True:\n"
            "        for i in range(10):\n"
            "            while True:\n"
            "                pass\n"
        )
        f1 = tmp_path / "simple.py"
        f1.write_text(simple)
        f2 = tmp_path / "complex.py"
        f2.write_text(complex_code)
        r1 = read_and_parse_code(str(f1))
        r2 = read_and_parse_code(str(f2))
        assert r2["complexity_score"] > r1["complexity_score"]

    def test_raw_code_matches_file(self, tmp_path):
        """Raw code must exactly match file content."""
        code = "x = 1\ny = 2\n"
        f = tmp_path / "test.py"
        f.write_text(code)
        result = read_and_parse_code(str(f))
        assert result["raw_code"] == code

    def test_raises_file_not_found(self):
        """Must raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            read_and_parse_code("nonexistent_file.py")

    def test_raises_syntax_error(self, tmp_path):
        """Must raise SyntaxError for invalid Python."""
        f = tmp_path / "bad.py"
        f.write_text("def foo(: pass")
        with pytest.raises(SyntaxError):
            read_and_parse_code(str(f))

    def test_empty_functions_for_no_functions(self, tmp_path):
        """Files with no functions must return empty list."""
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        result = read_and_parse_code(str(f))
        assert result["functions"] == []


# ── Agent Tests ───────────────────────────────────────────

class TestCodeUnderstandingAgent:

    def test_state_keys_populated(
            self, base_state, sample_clean_code):
        """All state keys must be populated after agent runs."""
        base_state["file_path"] = sample_clean_code
        result = code_understanding_node(base_state)
        assert result["raw_code"] != ""
        assert result["code_summary"] != ""
        assert isinstance(result["functions"], list)
        assert isinstance(result["imports"], list)
        assert isinstance(result["complexity_score"], int)

    def test_detects_functions_correctly(
            self, base_state, sample_clean_code):
        """Agent must detect all functions in the file."""
        base_state["file_path"] = sample_clean_code
        result = code_understanding_node(base_state)
        assert "add" in result["functions"]
        assert "subtract" in result["functions"]

    def test_summary_not_empty(
            self, base_state, sample_clean_code):
        """Agent must always produce a non-empty summary."""
        base_state["file_path"] = sample_clean_code
        result = code_understanding_node(base_state)
        assert len(result["code_summary"].strip()) > 0

    def test_status_remains_running(
            self, base_state, sample_clean_code):
        """Status must remain running after agent completes."""
        base_state["file_path"] = sample_clean_code
        result = code_understanding_node(base_state)
        assert result["status"] == "running"

    def test_logs_populated(
            self, base_state, sample_clean_code):
        """Logs must be populated after agent runs."""
        base_state["file_path"] = sample_clean_code
        result = code_understanding_node(base_state)
        assert len(result["logs"]) > 0

    def test_handles_missing_file_gracefully(
            self, base_state):
        """Agent must handle missing file without crashing."""
        base_state["file_path"] = "nonexistent.py"
        result = code_understanding_node(base_state)
        assert result["status"] == "failed"