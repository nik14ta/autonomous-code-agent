import os
import time
import git
from github import Github
from agent.state import AgentState
from agent.llm import get_llm
from langchain_core.prompts import PromptTemplate

def git_manager_node(state: AgentState) -> AgentState:
    """
    NODE 8 (Final): Git Manager
    Creates a branch, commits fixed files, and opens a Pull Request
    with a structured 'Explain the Fix' description.
    """
    logs = state.get("logs", [])
    logs.append("🚀 [Git Manager] Creating branch and committing fixes...")

    base_path = state["local_repo_path"]
    branch_name = f"agent/fix-{state['issue_number']}-{int(time.time())}"

    # Create and checkout a new branch
    repo = git.Repo(base_path)
    repo.git.checkout("-b", branch_name)
    logs.append(f"🌿 [Git Manager] Created branch '{branch_name}'")

    # Stage all modified files
    for file_path in state.get("modified_file_contents", {}).keys():
        repo.index.add([file_path])

    # Stage new test file
    if state.get("test_file_path"):
        try:
            repo.index.add([state["test_file_path"]])
        except:
            pass

    # Commit
    commit_message = f"fix: AI agent fix for issue #{state['issue_number']}\n\n{state['issue_title']}"
    repo.index.commit(commit_message)
    logs.append(f"✅ [Git Manager] Committed changes.")

    # Push the branch to GitHub
    origin = repo.remotes.origin
    origin.push(refspec=f"{branch_name}:{branch_name}")
    logs.append(f"⬆️  [Git Manager] Pushed branch to GitHub.")

    # Generate "Explain the Fix" PR summary using Gemini
    llm = get_llm(model="gemini-1.5-flash")
    prompt = PromptTemplate.from_template("""
    Write a professional GitHub Pull Request description for this bug fix.
    
    Issue: {title}
    Root Cause Analysis: {reasoning}
    Fix Plan: {fix_plan}
    Test Results: {tests_passed}/{tests_total} tests passed
    Files Changed: {files}
    
    Use this exact markdown structure:
    ## 🤖 Root Cause
    ## ✅ Fix Applied
    ## 🧪 Tests
    ## 📁 Files Changed
    
    Be concise and professional.
    """)
    chain = prompt | llm
    pr_summary = chain.invoke({
        "title": state["issue_title"],
        "reasoning": state.get("localization_reasoning", ""),
        "fix_plan": state.get("fix_plan", ""),
        "tests_passed": state.get("tests_passed", 0),
        "tests_total": state.get("tests_total", 0),
        "files": ", ".join(state.get("modified_file_contents", {}).keys()),
    }).content.strip()

    # Open the Pull Request via GitHub API
    g = Github(os.getenv("GITHUB_TOKEN"))
    gh_repo = g.get_repo(f"{state['repo_owner']}/{state['repo_name']}")
    pr = gh_repo.create_pull(
        title=f"🤖 Agent Fix: {state['issue_title'][:60]}",
        body=pr_summary,
        head=branch_name,
        base=gh_repo.default_branch
    )

    logs.append(f"🎉 [Git Manager] Pull Request opened: {pr.html_url}")

    return {
        **state,
        "branch_name": branch_name,
        "pr_url": pr.html_url,
        "pr_summary": pr_summary,
        "logs": logs,
        "current_node": "git_manager",
    }
