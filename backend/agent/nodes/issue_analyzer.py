import re
import uuid
from github import Github
from agent.state import AgentState
from agent.llm import get_llm
from langchain_core.prompts import PromptTemplate
import os

def issue_analyzer_node(state: AgentState) -> AgentState:
    """
    NODE 1: Issue Analyzer
    Parses the GitHub issue URL, fetches the issue content,
    and uses Gemini to classify the bug type.
    """
    logs = state.get("logs", [])
    logs.append("🔍 [Issue Analyzer] Fetching GitHub issue...")

    url = state["github_issue_url"]

    # Parse: https://github.com/owner/repo/issues/42
    match = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url)
    if not match:
        logs.append("❌ [Issue Analyzer] Invalid GitHub issue URL.")
        return {**state, "logs": logs, "current_node": "issue_analyzer"}

    repo_owner, repo_name, issue_number = match.group(1), match.group(2), int(match.group(3))

    # Fetch issue from GitHub API
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    issue = repo.get_issue(issue_number)

    logs.append(f"✅ [Issue Analyzer] Found issue #{issue_number}: '{issue.title}'")

    # Classify the bug type using Gemini
    llm = get_llm(model="gemini-2.0-flash")
    prompt = PromptTemplate.from_template("""
    Analyze this GitHub issue and classify the bug type.
    
    Title: {title}
    Body: {body}
    
    Respond with ONE of these categories:
    validation | logic | null_reference | performance | auth | database | other
    
    Respond with ONLY the category word, nothing else.
    """)
    chain = prompt | llm
    bug_type = chain.invoke({"title": issue.title, "body": issue.body or ""}).content.strip()

    logs.append(f"🏷️  [Issue Analyzer] Bug type classified as: '{bug_type}'")

    return {
        **state,
        "run_id": str(uuid.uuid4()),
        "issue_title": issue.title,
        "issue_body": issue.body or "",
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "issue_number": issue_number,
        "bug_type": bug_type,
        "logs": logs,
        "current_node": "issue_analyzer",
        "retry_count": 0,
        "approved": False,
    }
