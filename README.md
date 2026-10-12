# 🤖 Autonomous Code Agent

> A production-grade AI agent that reads GitHub Issues, analyzes your codebase, generates bug fixes, runs tests, and opens Pull Requests — with a human approval checkpoint before touching your code.

---

## ✨ Demo

```
GitHub Issue → Agent Analyzes → Fix Proposed → You Approve → PR Created
```

![Agent Workflow](https://img.shields.io/badge/LangGraph-Multi--Node%20Agent-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

---

## 🏗️ Architecture

```
GitHub Issue URL
      ↓
┌─────────────────────────────────────────────────────┐
│              LangGraph Agent Pipeline               │
│                                                     │
│  [1] Issue Analyzer    → Classifies bug type        │
│  [2] Repo Explorer     → Clones repo, maps files    │
│  [3] Bug Localizer     → Finds root cause (AST)     │
│  [4] Fix Planner       → Plain-English plan         │
│                                                     │
│  ⏸️  HUMAN APPROVAL CHECKPOINT                      │
│                                                     │
│  [5] Code Engineer     → Generates unified diffs    │
│  [6] Test Generator    → Writes pytest cases        │
│  [7] Test Runner       → Runs pytest in subprocess  │
│         ↓ FAIL (retry loop, max 3x)                 │
│  [8] Git Manager       → Branch → Commit → PR       │
└─────────────────────────────────────────────────────┘
```

---

## 🔥 Key Features

| Feature | Description |
|---|---|
| **Human-in-the-Loop** | Agent pauses after planning and waits for your approval before writing any code |
| **Unified Diffs** | Generates precise `before → after` patches, never blindly rewrites files |
| **Self-Correcting** | Test Runner loops back to Code Engineer on failure (max 3 retries) |
| **Real GitHub Integration** | Creates branch, commits, pushes, and opens PR via GitHub API |
| **Structured PR** | Every PR includes root cause analysis, test summary, and files changed |

---

## 🛠️ Tech Stack

- **Agent Framework:** LangGraph (multi-node state machine with `interrupt_before`)
- **LLM:** Google Gemini 2.0 Flash via LangChain
- **GitHub Integration:** PyGithub + GitPython
- **Backend:** FastAPI
- **Test Execution:** pytest via subprocess isolation

---

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/nik14ta/autonomous-code-agent.git
cd autonomous-code-agent/backend
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY="AIzaSy..."       # from aistudio.google.com/app/apikey
GITHUB_TOKEN="ghp_..."           # from github.com/settings/tokens
```

### 3. Run the server

```bash
uvicorn main:app --reload --port 8002
```

Open **http://localhost:8002/docs**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/agent/start` | Start the agent with a GitHub issue URL |
| `GET` | `/agent/{run_id}` | Get current agent state and logs |
| `POST` | `/agent/approve` | Resume agent after human approval |
| `POST` | `/agent/reject/{run_id}` | Cancel the agent run |

---

## 🔄 Workflow Example

**Step 1 — Start the agent:**
```json
POST /agent/start
{
  "github_issue_url": "https://github.com/your-org/your-repo/issues/42"
}
```

**Response (agent paused at checkpoint):**
```json
{
  "run_id": "abc-123",
  "status": "awaiting_approval",
  "bug_type": "validation",
  "suspicious_files": ["api/users.py", "schemas/user.py"],
  "confidence_score": 0.87,
  "fix_plan": "Add input validation before passing data to ORM..."
}
```

**Step 2 — Review the plan and approve:**
```json
POST /agent/approve
{
  "run_id": "abc-123"
}
```

**Response (completed):**
```json
{
  "status": "completed",
  "pr_url": "https://github.com/your-org/your-repo/pull/43",
  "tests_passed": 12,
  "tests_total": 12,
  "diffs": { "api/users.py": "--- a/api/users.py\n+++ b/api/users.py\n..." }
}
```

---

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI server
├── agent/
│   ├── state.py               # Shared AgentState TypedDict
│   ├── graph.py               # LangGraph state machine
│   ├── llm.py                 # LLM factory (Gemini / Demo mode)
│   └── nodes/
│       ├── issue_analyzer.py  # Node 1: Fetch & classify GitHub issue
│       ├── repo_explorer.py   # Node 2: Clone repo, list files
│       ├── bug_localizer.py   # Node 3: Two-pass bug localization
│       ├── fix_planner.py     # Node 4: Plain-English fix plan
│       ├── code_engineer.py   # Node 5: Generate unified diffs
│       ├── test_generator.py  # Node 6: Write pytest cases
│       ├── test_runner.py     # Node 7: Run pytest in subprocess
│       └── git_manager.py     # Node 8: Branch → Commit → PR
└── services/
    └── github_service.py      # GitHub API wrapper
```

---

## 📋 Resume Bullet Points

> **Autonomous Software Engineer Agent** | LangGraph, Gemini, FastAPI, GitHub API
> - Architected a **9-node LangGraph agent** that analyzes GitHub Issues, localizes bugs using two-pass LLM reasoning, and generates unified diff patches for Python repositories.
> - Implemented a **human-in-the-loop approval checkpoint** using LangGraph `interrupt_before` that pauses the agent after fix planning and resumes only on explicit engineer approval.
> - Engineered a **self-correcting test loop** that runs `pytest` via subprocess isolation, analyzes failures, and retries the fix up to 3 times before escalating to the Git Manager.
> - Automated the full **Git workflow** (branch creation, commit, PR) via the GitHub REST API, with structured PR descriptions including root cause analysis and test coverage summary.

---

## 🗺️ Roadmap

- [ ] **V2:** Next.js dashboard with real-time agent log streaming (SSE)
- [ ] **V2:** Side-by-side diff viewer with syntax highlighting  
- [ ] **V3:** GitHub App OAuth integration (no Personal Access Token needed)
- [ ] **V3:** JavaScript/TypeScript repository support
- [ ] **V4:** Docker sandbox for safe test execution

---

## 📄 License

MIT
