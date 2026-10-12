import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from agent.graph import agent_graph

app = FastAPI(title="Autonomous Software Engineer Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── In-memory run store (replace with PostgreSQL for production) ─
runs: dict = {}

class StartRequest(BaseModel):
    github_issue_url: str

class ApproveRequest(BaseModel):
    run_id: str

@app.get("/")
def root():
    return {"message": "Autonomous Software Engineer Agent is live!"}

@app.post("/agent/start")
async def start_agent(req: StartRequest):
    """
    Starts the agent pipeline.
    Runs until the human approval checkpoint (before code_engineer).
    Returns the run_id and the fix plan for the user to review.
    """
    run_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": run_id}}

    initial_state = {
        "github_issue_url": req.github_issue_url,
        "logs": [],
        "retry_count": 0,
        "approved": False,
    }

    # Run until interrupt (fix_planner → ⏸️ checkpoint)
    final_state = agent_graph.invoke(initial_state, config=config)

    # Store run for later approval
    runs[run_id] = {"config": config, "state": final_state}

    return {
        "run_id": run_id,
        "status": "awaiting_approval",
        "issue_title": final_state.get("issue_title"),
        "repo": f"{final_state.get('repo_owner')}/{final_state.get('repo_name')}",
        "bug_type": final_state.get("bug_type"),
        "suspicious_files": final_state.get("suspicious_files", []),
        "suspicious_functions": final_state.get("suspicious_functions", []),
        "confidence_score": final_state.get("confidence_score", 0),
        "fix_plan": final_state.get("fix_plan", ""),
        "logs": final_state.get("logs", []),
    }

@app.get("/agent/{run_id}")
def get_run_status(run_id: str):
    """Returns the current state of an agent run."""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    state = runs[run_id]["state"]
    return {
        "run_id": run_id,
        "current_node": state.get("current_node"),
        "logs": state.get("logs", []),
        "pr_url": state.get("pr_url", ""),
        "test_passed": state.get("test_passed", False),
        "tests_passed": state.get("tests_passed", 0),
        "tests_total": state.get("tests_total", 0),
        "diffs": state.get("diffs", {}),
    }

@app.post("/agent/approve")
async def approve_run(req: ApproveRequest):
    """
    Resumes the agent after human approval.
    The agent proceeds: Code Engineer → Test Generator → Test Runner → Git Manager → PR
    """
    if req.run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")

    config = runs[req.run_id]["config"]

    # Resume the graph from the checkpoint
    final_state = agent_graph.invoke(None, config=config)
    runs[req.run_id]["state"] = final_state

    return {
        "status": "completed",
        "pr_url": final_state.get("pr_url", ""),
        "tests_passed": final_state.get("tests_passed", 0),
        "tests_total": final_state.get("tests_total", 0),
        "test_output": final_state.get("test_output", ""),
        "diffs": final_state.get("diffs", {}),
        "pr_summary": final_state.get("pr_summary", ""),
        "logs": final_state.get("logs", []),
    }

@app.post("/agent/reject/{run_id}")
def reject_run(run_id: str):
    """Cancels an agent run."""
    if run_id in runs:
        del runs[run_id]
    return {"status": "rejected", "run_id": run_id}
