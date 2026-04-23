# agents/code_understanding_agent.py
from langchain_ollama import ChatOllama
from tools.read_and_parse_code import read_and_parse_code
from state.agent_state import AgentState
from utils.logger import log_event


# Initialize local LLM
llm = ChatOllama(model="llama3:8b", temperature=0)

SYSTEM_PROMPT = """You are a senior software architect. 
Your ONLY job is to understand what a given Python code does.

You must:
- Describe the overall purpose of the code in 2-3 sentences
- Explain what each function does briefly
- Identify the main logic flow
- Note any external dependencies used

You must NOT:
- Identify bugs or issues
- Suggest improvements
- Modify anything

Be concise, structured, and professional in your response.
"""


def code_understanding_node(state: AgentState) -> AgentState:
    """
    Agent node that reads and understands the submitted
    Python file. Populates code_summary, functions,
    imports, and complexity_score in the global state.

    Args:
        state (AgentState): The current pipeline state.

    Returns:
        AgentState: Updated state with understanding results.
    """
    log_event(
        agent="CodeUnderstandingAgent",
        event="start",
        detail=f"Reading file: {state['file_path']}"
    )

    try:
        # Use tool to read and parse the file
        parsed = read_and_parse_code(state["file_path"])

        log_event(
            agent="CodeUnderstandingAgent",
            event="tool_call",
            tool="read_and_parse_code",
            detail="File parsed successfully",
            input_data={"file_path": state["file_path"]},
            output_data={
                "functions": parsed["functions"],
                "imports": parsed["imports"],
                "complexity_score": parsed["complexity_score"]
            }
        )

        # Ask LLM to understand the code
        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Understand this Python code:\n\n{parsed['raw_code']}"
            }
        ])

        # Update global state
        state["raw_code"] = parsed["raw_code"]
        state["functions"] = parsed["functions"]
        state["imports"] = parsed["imports"]
        state["complexity_score"] = parsed["complexity_score"]
        state["code_summary"] = response.content
        state["status"] = "running"

        log_event(
            agent="CodeUnderstandingAgent",
            event="complete",
            detail="Code understanding complete",
            output_data={
                "summary_length": len(response.content),
                "functions_found": len(parsed["functions"])
            }
        )

        state["logs"].append(
            f"CodeUnderstandingAgent: Found "
            f"{len(parsed['functions'])} functions, "
            f"complexity={parsed['complexity_score']}"
        )

    except Exception as e:
        log_event(
            agent="CodeUnderstandingAgent",
            event="error",
            detail=str(e)
        )
        state["status"] = "failed"
        state["logs"].append(
            f"CodeUnderstandingAgent ERROR: {str(e)}"
        )

    return state