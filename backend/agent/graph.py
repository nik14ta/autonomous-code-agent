from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agent.state import AgentState
from agent.nodes.issue_analyzer import issue_analyzer_node
from agent.nodes.repo_explorer import repo_explorer_node
from agent.nodes.bug_localizer import bug_localizer_node
from agent.nodes.fix_planner import fix_planner_node
from agent.nodes.code_engineer import code_engineer_node
from agent.nodes.test_generator import test_generator_node
from agent.nodes.test_runner import test_runner_node
from agent.nodes.git_manager import git_manager_node

# ── Conditional edge: retry or proceed after tests ──────────────
def should_retry_or_proceed(state: AgentState) -> str:
    """After Test Runner: retry if failed (up to 3x), else go to Git Manager."""
    retry_count = state.get("retry_count", 0)
    if state.get("test_passed", False):
        return "git_manager"
    elif retry_count >= 3:
        # Max retries hit — still proceed (best-effort)
        return "git_manager"
    else:
        return "code_engineer"  # Loop back to re-generate the fix

def build_agent_graph():
    """
    Builds the full LangGraph state machine with:
    - 8 processing nodes
    - 1 human approval interrupt (after fix_planner)
    - 1 conditional retry loop (after test_runner)
    """
    memory = MemorySaver()  # Persists state across the interrupt
    graph = StateGraph(AgentState)

    # ── Register all nodes ──────────────────────────────────────
    graph.add_node("issue_analyzer",  issue_analyzer_node)
    graph.add_node("repo_explorer",   repo_explorer_node)
    graph.add_node("bug_localizer",   bug_localizer_node)
    graph.add_node("fix_planner",     fix_planner_node)
    graph.add_node("code_engineer",   code_engineer_node)
    graph.add_node("test_generator",  test_generator_node)
    graph.add_node("test_runner",     test_runner_node)
    graph.add_node("git_manager",     git_manager_node)

    # ── Define the flow ─────────────────────────────────────────
    graph.set_entry_point("issue_analyzer")
    graph.add_edge("issue_analyzer", "repo_explorer")
    graph.add_edge("repo_explorer",  "bug_localizer")
    graph.add_edge("bug_localizer",  "fix_planner")

    # ⏸️  HUMAN APPROVAL CHECKPOINT
    # The graph compiles with interrupt_before=["code_engineer"]
    # This means it STOPS before code_engineer and waits for resume()

    graph.add_edge("fix_planner",    "code_engineer")
    graph.add_edge("code_engineer",  "test_generator")
    graph.add_edge("test_generator", "test_runner")

    # ── Conditional retry loop ───────────────────────────────────
    graph.add_conditional_edges(
        "test_runner",
        should_retry_or_proceed,
        {
            "git_manager":    "git_manager",
            "code_engineer":  "code_engineer",
        }
    )

    graph.add_edge("git_manager", END)

    # Compile with interrupt BEFORE code_engineer (the approval checkpoint)
    return graph.compile(
        checkpointer=memory,
        interrupt_before=["code_engineer"]
    )

agent_graph = build_agent_graph()
