# 🤖 Autonomous Code Agent

> A production-grade Autonomous AI Software Engineer Agent that inspects GitHub Issues, clones & analyzes codebases, localizes bugs with AST reasoning, generates unified code diffs, runs test suites, and opens Pull Requests — featuring an interactive Human-in-the-Loop approval checkpoint before touching your repository.

---

## 🛠️ Complete Tech Stack & Languages

### 💻 Frontend (Client Dashboard)
- **Languages:** JavaScript (ES6+), HTML5, CSS3
- **Framework & Build:** React 19, Vite
- **UI Architecture & Design:** Modern Dark Studio Theme, Responsive Grid, Lucide Icons
- **State & Networking:** React Hooks (`useState`, `useEffect`, `useRef`), Fetch API with real-time polling/streaming

### ⚙️ Backend (API & Agent Pipeline)
- **Language:** Python 3.10+
- **Framework:** FastAPI, Uvicorn (ASGI Async Server)
- **Agent Orchestration:** LangGraph (StateGraph with `interrupt_before` approval checkpoint, MemorySaver checkpointer)
- **LLM & Tooling:** LangChain, Google Gemini 2.0 Flash / Pro, PromptTemplates
- **Version Control & Git Automation:** PyGithub, GitPython, GitHub REST API v3
- **Testing & Sandbox:** Pytest, Subprocess execution isolation

---

## ✨ System Architecture

```
GitHub Issue URL
      ↓
┌─────────────────────────────────────────────────────────────┐
│                 Frontend Dashboard (React + Vite)           │
│    • Live issue submission       • Real-time log terminal   │
│    • 9-Node progress tracker     • Human approval interface │
│    • Side-by-side diff viewer    • Verified PR link badge   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Port :8002)                │
│                                                             │
│   POST /agent/start    POST /agent/approve    GET /agent/:id│
└──────────────────────────────┬──────────────────────────────┘
                               │ StateGraph Execution
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Multi-Node Pipeline             │
│                                                             │
│   [1] Issue Analyzer   ➔ Fetches GitHub Issue & bug type   │
│   [2] Repo Explorer    ➔ Clones repo, maps Python files    │
│   [3] Bug Localizer    ➔ Two-pass LLM bug localization     │
│   [4] Fix Planner      ➔ Synthesizes plain-English plan    │
│                                                             │
│   ⏸️  HUMAN APPROVAL CHECKPOINT (LangGraph interrupt)       │
│                                                             │
│   [5] Code Engineer    ➔ Generates unified diff patches    │
│   [6] Test Generator   ➔ Writes pytest reproduction tests  │
│   [7] Test Runner      ➔ Executes pytest via subprocess    │
│          ↓ FAIL (Self-correcting retry loop, max 3x)        │
│   [8] Git Manager      ➔ Creates branch, commits & PR      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔥 Key Engineering Highlights

| Feature | Production Implementation |
|---|---|
| **Human-in-the-Loop Checkpoint** | Pauses agent execution after planning via LangGraph `interrupt_before`, waiting for human review |
| **Unified Diff Patching** | Synthesizes strict `before ➔ after` unified diffs instead of destructive file overwrites |
| **Self-Correcting Test Loop** | Executes `pytest` in an isolated subprocess; on failure, loops back to the Code Engineer (max 3 retries) |
| **Autonomous Git Automation** | Automates branch creation (`agent/fix-*`), file staging, commit messaging, and Pull Request creation |
| **Structured PR Documentation** | Pull Requests include root cause analysis, fix explanation, test coverage, and files modified |

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** v18+ & **npm**
- **Python** 3.10+
- **Git**

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate       # On Windows (or 'source venv/bin/activate' on macOS/Linux)
pip install -r requirements.txt
```

Configure your `backend/.env` file:
```env
GEMINI_API_KEY="AIzaSy..."    # From https://aistudio.google.com/app/apikey
GITHUB_TOKEN="ghp_..."        # From https://github.com/settings/tokens
```

Start the FastAPI backend:
```bash
uvicorn main:app --reload --port 8002
```
*API documentation available at `http://localhost:8002/docs`.*

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Open `http://localhost:5173/` in your browser to access the dashboard.*

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/agent/start` | Initiates agent run with GitHub issue URL (runs to approval checkpoint) |
| `GET` | `/agent/{run_id}` | Retrieves current state, execution logs, and diffs |
| `POST` | `/agent/approve` | Resumes agent after human approval (executes fix, tests, & PR creation) |
| `POST` | `/agent/reject/{run_id}` | Terminates and cancels the agent run |

---

## 📁 Repository Structure

```
autonomous-code-agent/
├── README.md                      # Complete system documentation
├── .gitignore                     # Ignores venv, node_modules, .env, and dist
│
├── backend/                       # Python & FastAPI Service
│   ├── main.py                    # REST API endpoints & lifecycle
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # API keys & configuration
│   ├── agent/
│   │   ├── state.py               # Shared AgentState TypedDict schema
│   │   ├── graph.py               # LangGraph state machine & checkpointing
│   │   ├── llm.py                 # LLM factory & mock demo fallbacks
│   │   └── nodes/
│   │       ├── issue_analyzer.py  # Node 1: Issue fetching & classification
│   │       ├── repo_explorer.py   # Node 2: Repository cloning & AST discovery
│   │       ├── bug_localizer.py   # Node 3: Suspect function localization
│   │       ├── fix_planner.py     # Node 4: Plain-English patch planner
│   │       ├── code_engineer.py   # Node 5: Unified diff synthesis
│   │       ├── test_generator.py  # Node 6: Pytest test case generator
│   │       ├── test_runner.py     # Node 7: Subprocess test execution
│   │       └── git_manager.py     # Node 8: Git branch, commit, & PR creation
│   └── services/
│       └── github_service.py      # GitHub REST API client wrapper
│
└── frontend/                      # React & Vite Dashboard
    ├── package.json               # Frontend dependencies & scripts
    ├── index.html                 # App HTML5 template
    ├── vite.config.js             # Vite development & build configuration
    └── src/
        ├── main.jsx               # React entry point
        ├── App.jsx                # Full-featured dashboard with approval flow
        └── index.css              # Dark theme styling, animations, & typography
```

---

## 📋 Resume Summary

> **Autonomous Software Engineer Agent** | React, Python, FastAPI, LangGraph, Gemini, GitHub API
> - Built a **full-stack agentic developer studio** (React, Vite, FastAPI) that autonomously resolves GitHub Issues from bug triage to Pull Request creation.
> - Implemented an **8-node LangGraph state machine** featuring a **Human-in-the-Loop approval checkpoint** (`interrupt_before`) ensuring engineer review prior to code synthesis.
> - Engineered an automated **self-correcting testing loop** that runs `pytest` in subprocess isolation and handles iterative refactoring upon test failure.
> - Automated end-to-end Git operations via the **GitHub REST API**, generating unified diff patches and Pull Requests with AI-generated root cause analyses.

---

## 📄 License
MIT License
