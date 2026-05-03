# agents/bug_analyst_agent.py
import json
from langchain_ollama import ChatOllama
from tools.run_linter_and_scanner import run_linter_and_scanner
from state.agent_state import AgentState
from utils.logger import log_event

# Initialize local LLM
llm = ChatOllama(model="llama3:8b", temperature=0)

SYSTEM_PROMPT = """You are a strict Python code quality expert.
Your ONLY job is to find what is WRONG with the given code.

You must identify:
- Logic bugs and errors
- Code smells and anti-patterns
- Security vulnerabilities
- Bad practices

For each issue you find, respond in this EXACT JSON format:
[
  {
    "line": <line_number_as_integer>,
    "type": "<bug|smell|security|style>",
    "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "description": "<clear description of the issue>"
  }
]

If no issues are found, return an empty list: []
Return ONLY the JSON list. No explanation. No markdown.
"""


def parse_bug_report(content: str) -> list:
    """
    Safely parses the LLM response into a list of bug dicts.

    Args:
        content (str): Raw LLM response string.

    Returns:
        list: Parsed list of bug report dicts.
    """
    try:
        # Strip markdown fences if present
        clean = content.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception:
        return [{
            "line": 0,
            "type": "unknown",
            "severity": "LOW",
            "description": content[:200]
        }]


def bug_analyst_node(state: AgentState) -> AgentState:
    """
    Agent node that analyzes the code for bugs, smells,
    and security issues using flake8, bandit, and LLM.

    Args:
        state (AgentState): The current pipeline state.

    Returns:
        AgentState: Updated state with bug_report,
                    lint_output, and security_issues.
    """
    log_event(
        agent="BugAnalystAgent",
        event="start",
        detail="Starting bug analysis"
    )

    try:
        # Use tool to run linter and security scanner
        tool_output = run_linter_and_scanner(
            state["file_path"]
        )

        log_event(
            agent="BugAnalystAgent",
            event="tool_call",
            tool="run_linter_and_scanner",
            detail="Linter and scanner completed",
            input_data={"file_path": state["file_path"]},
            output_data={
                "security_issues_count":
                    len(tool_output["security_issues"]),
                "lint_issues": tool_output["lint_output"][:100]
            }
        )

        # Ask LLM to reason about bugs using tool output
        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Code Summary: {state['code_summary']}

Linter Output:
{tool_output['lint_output']}

Security Scan Results:
{json.dumps(tool_output['security_issues'], indent=2)}

Raw Code:
{state['raw_code']}

Identify ALL bugs and issues as JSON.
"""
            }
        ])

        bug_report = parse_bug_report(response.content)

        # Update global state
        state["lint_output"] = tool_output["lint_output"]
        state["security_issues"] = tool_output["security_issues"]
        state["bug_report"] = bug_report

        log_event(
            agent="BugAnalystAgent",
            event="complete",
            detail=f"{len(bug_report)} issues found",
            output_data={"bug_count": len(bug_report)}
        )

        state["logs"].append(
            f"BugAnalystAgent: Found {len(bug_report)} "
            f"issues, {len(tool_output['security_issues'])} "
            f"security issues"
        )

    except Exception as e:
        log_event(
            agent="BugAnalystAgent",
            event="error",
            detail=str(e)
        )
        state["status"] = "failed"
        state["logs"].append(
            f"BugAnalystAgent ERROR: {str(e)}"
        )

    return state


 except Exception as e:
        log_event(
            agent="BugAnalystAgent",
            event="error",
            detail=str(e)
        )
        state["status"] = "failed"
        state["logs"].append(
            f"BugAnalystAgent ERROR: {str(e)}"
        )