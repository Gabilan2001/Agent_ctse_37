# agents/fix_generation_agent.py
import json
from langchain_ollama import ChatOllama
from tools.save_fixed_code import save_fixed_code
from state.agent_state import AgentState
from utils.logger import log_event

# Initialize local LLM
llm = ChatOllama(model="llama3:8b", temperature=0)

SYSTEM_PROMPT = """You are an expert Python developer.
You will receive the original buggy Python code and a 
detailed bug report.

Your job is to:
- Fix EVERY issue mentioned in the bug report
- Add an inline comment for each fix starting with # FIX:
- Keep the original logic and structure intact
- NOT add new features or change function names

Return ONLY the complete fixed Python code.
No explanations outside the code.
No markdown fences like ```python.
Just raw Python code only.
"""


def extract_fix_comments(code: str) -> list:
    """
    Extracts all inline FIX comments from the fixed code.

    Args:
        code (str): The fixed Python source code.

    Returns:
        list: A list of fix comment strings.
    """
    fixes = []
    for line in code.split("\n"):
        if "# FIX:" in line:
            fix = line[line.index("# FIX:"):].strip()
            fixes.append(fix)
    return fixes if fixes else ["Code reviewed and fixed."]


def fix_generation_node(state: AgentState) -> AgentState:
    """
    Agent node that generates a fixed version of the code
    based on the bug report from BugAnalystAgent.

    Args:
        state (AgentState): The current pipeline state.

    Returns:
        AgentState: Updated state with fixed_code,
                    fix_summary, and saved file path.
    """
    log_event(
        agent="FixGenerationAgent",
        event="start",
        detail=f"Fixing {len(state['bug_report'])} issues"
    )

    try:
        # Ask LLM to fix the code
        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Bug Report:
{json.dumps(state['bug_report'], indent=2)}

Original Code:
{state['raw_code']}

Generate the complete fixed Python code.
"""
            }
        ])

        fixed_code = response.content.strip()

        # Strip markdown fences if LLM adds them
        if fixed_code.startswith("```"):
            lines = fixed_code.split("\n")
            fixed_code = "\n".join(
                line for line in lines
                if not line.startswith("```")
            )

        # Use tool to save fixed code to disk
        saved_path = save_fixed_code(
            fixed_code=fixed_code,
            original_file_name=state["file_path"]
        )

        log_event(
            agent="FixGenerationAgent",
            event="tool_call",
            tool="save_fixed_code",
            detail="Fixed code saved",
            input_data={"original": state["file_path"]},
            output_data={"saved_path": saved_path}
        )

        fix_summary = extract_fix_comments(fixed_code)

        # Update global state
        state["fixed_code"] = fixed_code
        state["fix_summary"] = fix_summary

        log_event(
            agent="FixGenerationAgent",
            event="complete",
            detail=f"Fixed code saved to {saved_path}",
            output_data={
                "fixes_applied": len(fix_summary),
                "saved_path": saved_path
            }
        )

        state["logs"].append(
            f"FixGenerationAgent: Applied "
            f"{len(fix_summary)} fixes, "
            f"saved to {saved_path}"
        )

    except Exception as e:
        log_event(
            agent="FixGenerationAgent",
            event="error",
            detail=str(e)
        )
        state["status"] = "failed"
        state["logs"].append(
            f"FixGenerationAgent ERROR: {str(e)}"
        )

    return state