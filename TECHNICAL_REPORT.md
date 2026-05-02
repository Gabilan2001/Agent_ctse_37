# SE4010 – CTSE Assignment 2
# Technical Report: Multi-Agent Code Review System

**Group Members:** [Add your names]  
**Date:** April 2026  
**GitHub Repository:** [Add your repo URL]  

---

## 1. Problem Domain

### 1.1 Problem Statement
Software development teams face a significant challenge in maintaining consistent code quality. Manual code reviews are time-consuming, inconsistent, and prone to human error. Critical bugs, security vulnerabilities, and code smells are often missed, leading to technical debt and security risks.

### 1.2 Proposed Solution
We propose a locally-hosted Multi-Agent System (MAS) that automates the full code review pipeline. The system accepts a Python source file and autonomously:

1. Understands the code structure and purpose
2. Identifies bugs, smells, and security vulnerabilities
3. Generates a corrected version of the code
4. Validates the fix by generating and running unit tests
5. Produces a structured report of all findings

### 1.3 Why Multi-Agent?
This problem naturally decomposes into distinct specialized tasks. A single agent would struggle to simultaneously understand code, find bugs, fix them, and test them without losing focus or hallucinating. By separating these concerns into specialized agents, each agent can be given a tightly constrained role, reducing hallucinations and improving output quality.

---

## 2. System Architecture

### 2.1 Multi-Agent Architecture

The system implements a **Sequential Pipeline** pattern using LangGraph as the orchestration framework. Four specialized agents operate in sequence, each reading from and writing to a shared global state object.

```
[Python File Input]
        │
        ▼
┌─────────────────────────┐
│  CodeUnderstandingAgent │ → Understands code purpose & structure
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│    BugAnalystAgent      │ → Finds bugs & security vulnerabilities
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│   FixGenerationAgent    │ → Generates fixed version of code
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│   TestValidationAgent   │ → Tests & validates fixes
└─────────────────────────┘
        │
        ▼
[Report + Fixed Code Output]
```

### 2.2 Agent Roles & Responsibilities

| Agent | Role | Responsibility |
|---|---|---|
| `CodeUnderstandingAgent` | Analyst | Reads file, understands purpose, extracts structure |
| `BugAnalystAgent` | Inspector | Finds bugs, smells, and security vulnerabilities |
| `FixGenerationAgent` | Fixer | Generates corrected code with inline fix comments |
| `TestValidationAgent` | Validator | Generates & runs pytest tests on fixed code |

### 2.3 Orchestration Framework

**Framework:** LangGraph  
**Pattern:** Sequential Pipeline with Shared Global State  
**LLM:** llama3:8b via Ollama (fully local, zero cost)  

LangGraph was chosen because:
- Models pipeline as a directed graph of nodes
- Built-in TypedDict state management
- Native support for conditional edges
- Easy observability hooks at each node
- Works natively with Ollama via langchain-ollama

### 2.4 Workflow Diagram

```
main.py
  └── build_pipeline()
        ├── Node 1: CodeUnderstandingAgent
        │     ├── Tool: read_and_parse_code()
        │     └── LLM: Summarize code structure
        ├── Node 2: BugAnalystAgent
        │     ├── Tool: run_linter_and_scanner()
        │     └── LLM: Classify bugs from tool output
        ├── Node 3: FixGenerationAgent
        │     ├── LLM: Generate fixed code
        │     └── Tool: save_fixed_code()
        └── Node 4: TestValidationAgent
              ├── LLM: Generate pytest tests
              ├── Tool: run_tests()
              └── generate_report()
```

---

## 3. Agent Design

### 3.1 CodeUnderstandingAgent

**System Prompt Constraints:**
- ONLY describe what the code does
- Must NOT identify bugs or suggest improvements
- Must explain each function's purpose
- Must be concise and structured

**Reasoning Logic:**  
The agent first uses the `read_and_parse_code` tool to extract structural information (functions, imports, complexity). It then passes the raw code to the LLM with strict constraints to produce a factual summary without making any quality judgements.

**Interaction Strategy:**  
Passes `code_summary`, `functions`, `imports`, and `complexity_score` to the next agent as context.

---

### 3.2 BugAnalystAgent

**System Prompt Constraints:**
- ONLY identify what is wrong
- Must classify by type: bug/smell/security/style
- Must assign severity: LOW/MEDIUM/HIGH/CRITICAL
- Must return structured JSON output only
- Must NOT fix anything

**Reasoning Logic:**  
The agent combines tool output (flake8 lint results + bandit security scan) with LLM reasoning to produce a comprehensive bug report. The tool output grounds the LLM, preventing hallucination of non-existent bugs.

**Interaction Strategy:**  
Uses `code_summary` from Agent 1 as context to reason about bugs more intelligently. Passes `bug_report[]` to the next agent.

---

### 3.3 FixGenerationAgent

**System Prompt Constraints:**
- Must fix EVERY issue in the bug report
- Must add `# FIX:` inline comment for each change
- Must NOT change original logic or add new features
- Must return ONLY raw Python code, no markdown fences

**Reasoning Logic:**  
The agent receives both the original code and the structured bug report. By providing the bug report as structured JSON, the LLM can systematically address each issue rather than making broad rewrites.

**Interaction Strategy:**  
Saves fixed code to disk using `save_fixed_code` tool. Passes `fixed_code` and `fix_summary` to next agent.

---

### 3.4 TestValidationAgent

**System Prompt Constraints:**
- Must write tests for ALL functions
- Must cover happy path AND edge cases
- Must import from `solution` module
- Must return ONLY valid pytest code

**Reasoning Logic:**  
The agent uses the `code_summary` from Agent 1 to understand what each function is supposed to do, then generates appropriate test cases. Tests are executed in an isolated temporary directory to prevent side effects.

**Interaction Strategy:**  
Uses `run_tests` tool to execute generated tests. Produces final markdown report summarizing all findings.

---

## 4. Custom Tools

### 4.1 `read_and_parse_code` (Student 1)

**Purpose:** Reads a Python file and extracts structural information using Python's built-in AST module.

**APIs/Interactions:** Local file system read, Python `ast` module for static analysis.

**Example Usage:**
```python
result = read_and_parse_code("mycode.py")
# Returns:
# {
#   "raw_code": "def hello(): ...",
#   "functions": ["hello"],
#   "imports": ["os"],
#   "complexity_score": 2
# }
```

---

### 4.2 `run_linter_and_scanner` (Student 2)

**Purpose:** Runs flake8 (style/bug linting) and bandit (security scanning) on a Python file via subprocess.

**APIs/Interactions:** Subprocess calls to `flake8` and `bandit` CLI tools. Parses bandit's JSON output.

**Example Usage:**
```python
result = run_linter_and_scanner("mycode.py")
# Returns:
# {
#   "lint_output": "mycode.py:1:1: F401 'os' imported...",
#   "security_issues": [
#     {"line": 5, "issue": "Hardcoded password",
#      "severity": "HIGH"}
#   ]
# }
```

---

### 4.3 `save_fixed_code` (Student 3)

**Purpose:** Saves LLM-generated fixed Python code to the outputs/ directory with a timestamped filename.

**APIs/Interactions:** Local file system write.

**Example Usage:**
```python
path = save_fixed_code(fixed_code, "original.py")
# Returns: "outputs/fixed_20260423_145448_original.py"
```

---

### 4.4 `run_tests` (Student 4)

**Purpose:** Saves generated test code and fixed code to a temporary directory and executes pytest via subprocess, capturing pass/fail results.

**APIs/Interactions:** Subprocess call to `pytest` CLI. Uses Python's `tempfile` module for isolation.

**Example Usage:**
```python
result = run_tests(test_code, fixed_code)
# Returns:
# {
#   "passed": 10,
#   "failed": 2,
#   "errors": ["FAILED test_divide_by_zero"]
# }
```

---

## 5. State Management

### 5.1 Global State Structure

The system uses a LangGraph `TypedDict` as the shared global state that flows through every agent:

```python
class AgentState(TypedDict):
    # Input
    file_path: str
    raw_code: str
    # CodeUnderstandingAgent output
    code_summary: str
    functions: List[str]
    imports: List[str]
    complexity_score: int
    # BugAnalystAgent output
    bug_report: List[dict]
    lint_output: str
    security_issues: List[dict]
    # FixGenerationAgent output
    fixed_code: str
    fix_summary: List[str]
    # TestValidationAgent output
    test_code: str
    test_results: dict
    final_report_path: str
    # System-wide
    logs: List[str]
    status: str
```

### 5.2 Context Passing Between Agents

Each agent receives the FULL state object, reads only the keys it needs, and writes its outputs back to the state. LangGraph ensures the updated state is passed to the next node automatically.

```
Agent 1 writes → code_summary, functions, imports, complexity_score
Agent 2 reads  → code_summary, raw_code
Agent 2 writes → bug_report, lint_output, security_issues
Agent 3 reads  → raw_code, bug_report
Agent 3 writes → fixed_code, fix_summary
Agent 4 reads  → fixed_code, code_summary
Agent 4 writes → test_code, test_results, final_report_path
```

### 5.3 No Context Loss
By passing the complete state dictionary at each step, no information is lost between agent handoffs. Every agent has access to all outputs from all previous agents.

---

## 6. Evaluation Methodology

### 6.1 Testing Strategy
The system uses a hybrid evaluation approach:

**Rule-Based Validation** — for deterministic checks:
- File existence, correct keys in output
- Type checking (list, int, str)
- Error handling (FileNotFoundError, ValueError)
- Tool output structure validation

**Functional Testing** — for agent behavior:
- Agent produces non-empty outputs
- State keys are correctly populated
- Status transitions correctly
- Error handling works gracefully

### 6.2 Test Results

| Student | Agent | Tests | Passed | Failed |
|---|---|---|---|---|
| Student 1 | CodeUnderstandingAgent | 14 | 14 | 0 |
| Student 2 | BugAnalystAgent | 12 | 12 | 0 |
| Student 3 | FixGenerationAgent | 12 | 12 | 0 |
| Student 4 | TestValidationAgent | 12 | 12 | 0 |
| **Total** | | **50** | **50** | **0** |

### 6.3 Performance Analysis

**Pipeline execution on buggy_code.py:**
- Functions detected: 9
- Bugs found: 16
- Security issues: 7
- Fixes applied: 10
- Tests generated: 70 lines
- Tests passed: 14/19
- Total execution time: ~90 seconds

### 6.4 Reliability Analysis
- All 50 unit tests pass consistently
- Pipeline handles missing files gracefully
- Pipeline handles invalid Python gracefully
- Agents fail safely and log errors to state

---

## 7. Individual Contributions

### Student 1 — [Name]
**Agent:** `CodeUnderstandingAgent`  
**Tool:** `read_and_parse_code`  
**Tests:** `tests/test_code_understanding.py` (14 tests)  

**Challenges Faced:**
- Tuning the system prompt to prevent the agent from mentioning bugs (it kept wanting to analyze quality)
- Handling edge cases in AST parsing for complex files

---

### Student 2 — [Name]
**Agent:** `BugAnalystAgent`  
**Tool:** `run_linter_and_scanner`  
**Tests:** `tests/test_bug_analyst.py` (12 tests)  

**Challenges Faced:**
- Parsing bandit's JSON output reliably across different versions
- Getting the LLM to return valid JSON consistently (solved with strict system prompt + parse_bug_report fallback function)

---

### Student 3 — [Name]
**Agent:** `FixGenerationAgent`  
**Tool:** `save_fixed_code`  
**Tests:** `tests/test_fix_generation.py` (12 tests)  

**Challenges Faced:**
- LLM kept returning markdown code fences (```python) despite instructions — solved with post-processing strip function
- Ensuring the fixed code preserved original logic while fixing all reported issues

---

### Student 4 — [Name]
**Agent:** `TestValidationAgent`  
**Tool:** `run_tests`  
**Tests:** `tests/test_validation_agent.py` (12 tests)  

**Challenges Faced:**
- Running tests in isolation without polluting the project directory — solved with tempfile module
- LLM-generated tests sometimes imported modules incorrectly — solved with strict import instructions in system prompt

---

## 8. GitHub Repository

**Repository URL:** [Add your GitHub URL here]

**Repository Structure:**
```
mas-code-review/
├── agents/          # 4 agent implementations
├── tools/           # 4 custom Python tools
├── state/           # Global state definition
├── graph/           # LangGraph pipeline
├── tests/           # 50 unit tests
├── outputs/         # Generated reports & fixed code
├── logs/            # Execution logs
├── api.py           # FastAPI backend
├── main.py          # CLI entry point
└── requirements.txt
```
