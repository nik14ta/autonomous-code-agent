import os
from agent.state import AgentState
from agent.llm import get_llm
from langchain_core.prompts import PromptTemplate

def fix_planner_node(state: AgentState) -> AgentState:
    """
    NODE 4: Fix Planner
    Creates a human-readable plan of what needs to change.
    This runs BEFORE the human approval checkpoint.
    No code is written yet — only a plan.
    """
    logs = state.get("logs", [])
    logs.append("📋 [Fix Planner] Creating fix plan...")

    base_path = state["local_repo_path"]

    # Read suspicious files
    file_contents_str = ""
    for f in state.get("suspicious_files", []):
        try:
            with open(os.path.join(base_path, f), "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()[:3000]
            file_contents_str += f"\n\n--- FILE: {f} ---\n{content}"
        except:
            pass

    llm = get_llm()
    prompt = PromptTemplate.from_template("""
    You are a senior software engineer creating a fix plan.
    
    Bug: {title}
    Description: {body}
    Suspicious functions: {functions}
    
    Relevant code:
    {file_contents}
    
    Create a concise fix plan with:
    1. Root cause (1 sentence)
    2. Proposed fix (bullet points of what changes are needed, NO actual code)
    3. Files to modify (list)
    4. New tests needed (list)
    
    Be specific but brief. This plan will be shown to a human for approval.
    """)

    chain = prompt | llm
    result = chain.invoke({
        "title": state["issue_title"],
        "body": state["issue_body"],
        "functions": state.get("suspicious_functions", []),
        "file_contents": file_contents_str
    })

    fix_plan = result.content.strip()
    logs.append("📋 [Fix Planner] Plan created. Waiting for human approval...")
    logs.append("⏸️  [CHECKPOINT] Agent paused. Please review and approve the plan.")

    return {
        **state,
        "fix_plan": fix_plan,
        "files_to_modify": state.get("suspicious_files", []),
        "proposed_changes_summary": fix_plan,
        "logs": logs,
        "current_node": "fix_planner",
    }
