import os
import git
from agent.state import AgentState

CLONE_DIR = "cloned_repos"

FRAMEWORK_MARKERS = {
    "fastapi": ["fastapi", "uvicorn"],
    "django": ["django"],
    "flask": ["flask"],
}

def repo_explorer_node(state: AgentState) -> AgentState:
    """
    NODE 2: Repository Explorer
    Clones the repo locally, lists all Python files,
    identifies test files, and detects the framework.
    """
    logs = state.get("logs", [])
    logs.append(f"📁 [Repo Explorer] Cloning '{state['repo_owner']}/{state['repo_name']}'...")

    repo_url = f"https://oauth2:{os.getenv('GITHUB_TOKEN')}@github.com/{state['repo_owner']}/{state['repo_name']}.git"
    local_path = os.path.join(CLONE_DIR, state["repo_name"])

    # Clone or pull the repo
    os.makedirs(CLONE_DIR, exist_ok=True)
    if os.path.exists(local_path):
        git.Repo(local_path).remotes.origin.pull()
        logs.append(f"🔄 [Repo Explorer] Repo already exists. Pulled latest changes.")
    else:
        git.Repo.clone_from(repo_url, local_path)
        logs.append(f"✅ [Repo Explorer] Cloned successfully to '{local_path}'.")

    # Walk the directory and list all Python files
    all_files = []
    test_files = []
    for root, dirs, files in os.walk(local_path):
        # Skip hidden and virtual environment directories
        dirs[:] = [d for d in dirs if d not in [".git", "venv", "__pycache__", "node_modules", ".env"]]
        for file in files:
            if file.endswith(".py"):
                rel_path = os.path.relpath(os.path.join(root, file), local_path)
                all_files.append(rel_path)
                if "test" in file.lower() or "test" in root.lower():
                    test_files.append(rel_path)

    logs.append(f"📊 [Repo Explorer] Found {len(all_files)} Python files, {len(test_files)} test files.")

    # Detect framework from requirements.txt or setup.py
    framework = "unknown"
    req_path = os.path.join(local_path, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            content = f.read().lower()
        for fw, markers in FRAMEWORK_MARKERS.items():
            if any(m in content for m in markers):
                framework = fw
                break

    logs.append(f"🔧 [Repo Explorer] Detected framework: '{framework}'")

    return {
        **state,
        "local_repo_path": local_path,
        "all_files": all_files,
        "test_files": test_files,
        "framework": framework,
        "logs": logs,
        "current_node": "repo_explorer",
    }
