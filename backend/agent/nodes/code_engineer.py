import os
import difflib
from agent.state import AgentState
from agent.llm import get_llm
from langchain_core.prompts import PromptTemplate

def code_engineer_node(state: AgentState) -> AgentState:
    """
    NODE 5: Code Engineer
    Runs AFTER human approval.
    Generates the actual fixed code and produces unified diffs.
    """
    logs = state.get("logs", [])
    logs.append("💻 [Code Engineer] Generating code fixes...")

    base_path = state["local_repo_path"]
    llm = get_llm()
    diffs = {}
    modified_contents = {}

    for file_path in state.get("files_to_modify", []):
        full_path = os.path.join(base_path, file_path)
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()
        except:
            logs.append(f"⚠️  [Code Engineer] Could not read '{file_path}', skipping.")
            continue

        logs.append(f"💻 [Code Engineer] Fixing '{file_path}'...")

        prompt = PromptTemplate.from_template("""
        You are a senior software engineer.
        
        Bug: {title}
        Fix Plan: {fix_plan}
        
        File: {file_path}
        Current content:
        {content}
        
        Return the COMPLETE fixed version of this file.
        Only fix what the bug requires. Do not refactor unrelated code.
        Return ONLY the raw Python code, no markdown, no backticks.
        """)

        chain = prompt | llm
        result = chain.invoke({
            "title": state["issue_title"],
            "fix_plan": state.get("fix_plan", ""),
            "file_path": file_path,
            "content": original_content[:6000]
        })

        fixed_content = result.content.strip()
        # Strip markdown if LLM adds it
        if fixed_content.startswith("```"):
            lines = fixed_content.split("\n")
            fixed_content = "\n".join(lines[1:-1])

        # Generate a unified diff
        diff = "".join(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            fixed_content.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        ))

        diffs[file_path] = diff
        modified_contents[file_path] = fixed_content
        logs.append(f"✅ [Code Engineer] Diff generated for '{file_path}' ({len(diff.splitlines())} lines changed)")

    return {
        **state,
        "diffs": diffs,
        "modified_file_contents": modified_contents,
        "logs": logs,
        "current_node": "code_engineer",
    }
