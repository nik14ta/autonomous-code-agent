import os
import json
from agent.state import AgentState
from agent.llm import get_llm
from langchain_core.prompts import PromptTemplate

MAX_FILES_TO_SEND = 30  # Avoid token overflow

def _read_file(base_path: str, rel_path: str) -> str:
    """Reads a file and returns its content (truncated if too large)."""
    try:
        with open(os.path.join(base_path, rel_path), "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content[:3000]  # Limit per file
    except:
        return ""

def bug_localizer_node(state: AgentState) -> AgentState:
    """
    NODE 3: Bug Localizer
    Uses Gemini to identify which files and functions
    are most likely causing the reported bug.
    """
    logs = state.get("logs", [])
    logs.append("🎯 [Bug Localizer] Analyzing codebase to locate the bug...")

    base_path = state["local_repo_path"]
    all_files = state["all_files"]

    # Step 1: Give Gemini the file list and ask it to narrow down suspects
    llm = get_llm(model="gemini-1.5-flash")
    file_list_str = "\n".join(all_files[:MAX_FILES_TO_SEND])

    prompt_narrow = PromptTemplate.from_template("""
    You are an expert software engineer.
    
    Bug Report:
    Title: {title}
    Description: {body}
    Bug Type: {bug_type}
    
    Repository files:
    {file_list}
    
    Which files are most likely related to this bug?
    Return a JSON list of up to 5 file paths.
    Example: ["api/users.py", "schemas/user.py"]
    Return ONLY the JSON list.
    """)

    chain_narrow = prompt_narrow | llm
    result = chain_narrow.invoke({
        "title": state["issue_title"],
        "body": state["issue_body"],
        "bug_type": state["bug_type"],
        "file_list": file_list_str
    })

    try:
        suspicious_files = json.loads(result.content.strip())
    except:
        suspicious_files = all_files[:3]

    logs.append(f"🎯 [Bug Localizer] Narrowed to {len(suspicious_files)} suspicious files: {suspicious_files}")

    # Step 2: Read the suspicious files and ask Gemini for specific functions
    file_contents_str = ""
    for f in suspicious_files:
        content = _read_file(base_path, f)
        if content:
            file_contents_str += f"\n\n--- FILE: {f} ---\n{content}"

    prompt_functions = PromptTemplate.from_template("""
    Bug Report: {title}
    Description: {body}
    
    Relevant file contents:
    {file_contents}
    
    Identify:
    1. The specific function(s) or class(es) most likely causing this bug.
    2. Your confidence score (0.0 to 1.0).
    3. Your reasoning (1-2 sentences).
    
    Return ONLY valid JSON with keys: "functions", "confidence", "reasoning"
    Example: {{"functions": ["validate_user", "create_user"], "confidence": 0.87, "reasoning": "..."}}
    """)

    chain_fn = prompt_functions | llm
    result_fn = chain_fn.invoke({
        "title": state["issue_title"],
        "body": state["issue_body"],
        "file_contents": file_contents_str
    })

    try:
        parsed = json.loads(result_fn.content.strip())
        suspicious_functions = parsed.get("functions", [])
        confidence_score = float(parsed.get("confidence", 0.5))
        reasoning = parsed.get("reasoning", "")
    except:
        suspicious_functions = []
        confidence_score = 0.5
        reasoning = "Could not parse localization result."

    logs.append(f"🎯 [Bug Localizer] Suspicious functions: {suspicious_functions}")
    logs.append(f"🎯 [Bug Localizer] Confidence: {confidence_score:.0%} — {reasoning}")

    return {
        **state,
        "suspicious_files": suspicious_files,
        "suspicious_functions": suspicious_functions,
        "confidence_score": confidence_score,
        "localization_reasoning": reasoning,
        "logs": logs,
        "current_node": "bug_localizer",
    }
