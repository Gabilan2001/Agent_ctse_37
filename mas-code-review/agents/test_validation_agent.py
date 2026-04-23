# agents/test_validation_agent.py
import os
from datetime import datetime
from langchain_ollama import ChatOllama
from tools.run_tests import run_tests
from state.agent_state import AgentState
from utils.logger import log_event

# Initialize local LLM
llm = ChatOllama(model="llama3:8b", temperature=0)

SYSTEM_PROMPT = """You are a Python testing expert.
You will receive a summary of what the code does and
the fixed Python code.

Your job is to:
- Write pytest unit tests for ALL functions in the code
- Cover happy path AND edge cases for each function
- Use clear test function names: test_<function>_<scenario>
- Import the function from solution module like:
  from solution import <function_name>

Return ONLY valid pytest code.
No explanations. No markdown fences. Just raw Python code.
"""


def generate_report(state: AgentState) -> str:
    """
    Generates a markdown report summarizing the full
    pipeline results and saves it to outputs/.

    Args:
        state (AgentState): The completed pipeline state.

    Returns:
        str: Path to the saved markdown report file.
    """
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"outputs/report_{timestamp}.md"

    passed = state["test_results"].get("passed", 0)
    failed = state["test_results"].get("failed", 0)
    total = passed + failed

    report = f"""# MAS Code Review Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Code Summary
{state["code_summary"]}

## Code Metrics
- **Functions Found:** {len(state["functions"])}
- **Imports:** {", ".join(state["imports"]) or "None"}
- **Complexity Score:** {state["complexity_score"]}

## Bug Report
**Total Issues Found:** {len(state["bug_report"])}

| Line | Type | Severity | Description |
|------|------|----------|-------------|
"""

    for bug in state["bug_report"]:
        report += (
            f"| {bug.get('line', 0)} "
            f"| {bug.get('type', '')} "
            f"| {bug.get('severity', '')} "
            f"| {bug.get('description', '')} |\n"
        )

    report += f"\n## Security Issues\n"
    report += f"**Total Security Issues:** {len(state['security_issues'])}\n"

    for issue in state["security_issues"]:
        report += (
            f"- **Line {issue.get('line', 0)}:** "
            f"{issue.get('issue', '')} "
            f"({issue.get('severity', '')})\n"
        )

    report += "\n## Fix Summary\n"
    for fix in state["fix_summary"]:
        report += f"- {fix}\n"

    report += f"\n## Test Results\n"
    report += f"- **Passed:** {passed}/{total}\n"
    report += f"- **Failed:** {failed}/{total}\n"

    if state["test_results"].get("errors"):
        report += "\n### Errors\n"
        for err in state["test_results"]["errors"]:
            report += f"- {err}\n"

    report += "\n## Execution Logs\n```\n"
    for log in state["logs"]:
        report += f"{log}\n"
    report += "```\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report_path


def test_validation_node(state: AgentState) -> AgentState:
    """
    Agent node that generates pytest unit tests for the
    fixed code and executes them to validate correctness.

    Args:
        state (AgentState): The current pipeline state.

    Returns:
        AgentState: Updated state with test_code,
                    test_results, and final_report_path.
    """
    log_event(
        agent="TestValidationAgent",
        event="start",
        detail="Generating and running tests"
    )

    try:
        # Ask LLM to generate tests
        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Code Summary: {state['code_summary']}

Fixed Code:
{state['fixed_code']}

Write comprehensive pytest tests.
"""
            }
        ])

        test_code = response.content.strip()

        # Strip markdown fences if LLM adds them
        if test_code.startswith("```"):
            lines = test_code.split("\n")
            test_code = "\n".join(
                line for line in lines
                if not line.startswith("```")
            )

        log_event(
            agent="TestValidationAgent",
            event="tool_call",
            tool="run_tests",
            detail="Running generated tests",
            input_data={
                "test_lines": len(test_code.split("\n"))
            }
        )

        # Use tool to run the tests
        results = run_tests(
            test_code=test_code,
            fixed_code=state["fixed_code"]
        )

        # Generate final markdown report
        state["test_code"] = test_code
        state["test_results"] = results
        report_path = generate_report(state)
        state["final_report_path"] = report_path
        state["status"] = "completed"

        log_event(
            agent="TestValidationAgent",
            event="complete",
            detail=(
                f"Tests: {results['passed']} passed, "
                f"{results['failed']} failed"
            ),
            output_data={
                "passed": results["passed"],
                "failed": results["failed"],
                "report": report_path
            }
        )

        state["logs"].append(
            f"TestValidationAgent: "
            f"{results['passed']} passed, "
            f"{results['failed']} failed. "
            f"Report: {report_path}"
        )

    except Exception as e:
        log_event(
            agent="TestValidationAgent",
            event="error",
            detail=str(e)
        )
        state["status"] = "failed"
        state["logs"].append(
            f"TestValidationAgent ERROR: {str(e)}"
        )

    return state