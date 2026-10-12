from typing import TypedDict, List, Optional, Dict

class AgentState(TypedDict):
    """Shared memory across all 9 LangGraph nodes."""

    # ── Inputs ──────────────────────────────────────────
    github_issue_url: str       # e.g. "https://github.com/nik14ta/hrms/issues/42"
    run_id: str                 # Unique ID for this agent run (stored in DB)

    # ── Issue Analyzer outputs ───────────────────────────
    issue_title: str
    issue_body: str
    repo_owner: str
    repo_name: str
    issue_number: int
    bug_type: str               # e.g. "validation", "logic", "null_reference"

    # ── Repo Explorer outputs ────────────────────────────
    local_repo_path: str        # Local clone path
    all_files: List[str]        # All Python file paths
    test_files: List[str]       # Identified test files
    framework: str              # e.g. "fastapi", "django", "flask"

    # ── Bug Localizer outputs ────────────────────────────
    suspicious_files: List[str]
    suspicious_functions: List[str]
    confidence_score: float     # e.g. 0.87
    localization_reasoning: str

    # ── Fix Planner outputs (before checkpoint) ──────────
    fix_plan: str               # Plain-English plan
    files_to_modify: List[str]
    proposed_changes_summary: str

    # ── Human Approval ───────────────────────────────────
    approved: bool              # Set to True by POST /approve

    # ── Code Engineer outputs ────────────────────────────
    diffs: Dict[str, str]       # { "api/users.py": "unified diff string" }
    modified_file_contents: Dict[str, str]  # Full file contents after patch

    # ── Test Generator outputs ───────────────────────────
    generated_tests: str        # New pytest code
    test_file_path: str         # Where the test will be written

    # ── Test Runner outputs ──────────────────────────────
    test_passed: bool
    test_output: str            # Full pytest stdout
    tests_total: int
    tests_passed: int
    retry_count: int

    # ── Git Manager outputs ──────────────────────────────
    branch_name: str
    pr_url: str
    pr_summary: str             # "Explain the Fix" markdown

    # ── Real-time logs (streamed to frontend) ────────────
    logs: List[str]
    current_node: str
