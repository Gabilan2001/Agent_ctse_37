# graph/pipeline.py
from langgraph.graph import StateGraph, END
from state.agent_state import AgentState
from agents.code_understanding_agent import code_understanding_node
from agents.bug_analyst_agent import bug_analyst_node
from agents.fix_generation_agent import fix_generation_node
from agents.test_validation_agent import validation_node


def build_pipeline():
    """
    Builds and compiles the LangGraph pipeline connecting
    all 4 agents in a sequential workflow.

    Returns:
        CompiledGraph: The compiled LangGraph pipeline
                       ready for execution.
    """
    graph = StateGraph(AgentState)

    # Register all agent nodes
    graph.add_node(
        "CodeUnderstandingAgent",
        code_understanding_node
    )
    graph.add_node(
        "BugAnalystAgent",
        bug_analyst_node
    )
    graph.add_node(
        "FixGenerationAgent",
        fix_generation_node
    )
    graph.add_node(
        "TestValidationAgent",
        validation_node
    )

    # Define sequential edges
    graph.set_entry_point("CodeUnderstandingAgent")
    graph.add_edge("CodeUnderstandingAgent", "BugAnalystAgent")
    graph.add_edge("BugAnalystAgent", "FixGenerationAgent")
    graph.add_edge("FixGenerationAgent", "TestValidationAgent")
    graph.add_edge("TestValidationAgent", END)

    return graph.compile()