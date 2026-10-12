import os
import subprocess
from agent.state import AgentState

def test_runner_node(state: AgentState) -> AgentState:
    """
    NODE 7: Test Runner
    1. Writes fixed files and new tests to the local repo.
    2. Runs pytest via subprocess.
    3. Parses test output to determine pass/fail.
    """
    logs = state.get("logs", [])
    logs.append("🏃 [Test Runner] Applying fixes and running pytest...")

    base_path = state["local_repo_path"]

    # Write fixed file contents to disk
    for file_path, content in state.get("modified_file_contents", {}).items():
        full_path = os.path.join(base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        logs.append(f"📝 [Test Runner] Wrote fix to '{file_path}'")

    # Append new tests to the test file
    if state.get("generated_tests") and state.get("test_file_path"):
        test_full_path = os.path.join(base_path, state["test_file_path"])
        with open(test_full_path, "a", encoding="utf-8") as f:
            f.write("\n\n# ── AI Generated Tests ──\n")
            f.write(state["generated_tests"])
        logs.append(f"🧪 [Test Runner] Appended new tests to '{state['test_file_path']}'")

    # Run pytest
    logs.append("🏃 [Test Runner] Running pytest...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--tb=short", "-q"],
            cwd=base_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        test_output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        test_output = "ERROR: pytest timed out after 120 seconds."
        logs.append("⏰ [Test Runner] pytest timed out.")
        return {**state, "test_passed": False, "test_output": test_output, "tests_total": 0, "tests_passed": 0, "logs": logs, "current_node": "test_runner"}

    # Parse results
    test_passed = result.returncode == 0
    tests_passed = 0
    tests_total = 0

    for line in test_output.splitlines():
        if "passed" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "passed":
                    try:
                        tests_passed = int(parts[i - 1])
                    except:
                        pass
                if p in ("failed", "error"):
                    try:
                        tests_total += int(parts[i - 1])
                    except:
                        pass
            tests_total += tests_passed

    status = "✅ PASSED" if test_passed else "❌ FAILED"
    logs.append(f"🏃 [Test Runner] {status} — {tests_passed}/{tests_total} tests passed")

    return {
        **state,
        "test_passed": test_passed,
        "test_output": test_output,
        "tests_total": tests_total,
        "tests_passed": tests_passed,
        "logs": logs,
        "current_node": "test_runner",
    }
