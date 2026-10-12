import os
from agent.state import AgentState
from agent.llm import get_llm
from langchain_core.prompts import PromptTemplate

def test_generator_node(state: AgentState) -> AgentState:
    """
    NODE 6: Test Generator
    Writes new pytest test cases that reproduce the bug
    and verify the fix works correctly.
    """
    logs = state.get("logs", [])
    logs.append("🧪 [Test Generator] Writing new test cases...")

    llm = get_llm()
    base_path = state["local_repo_path"]

    # Read existing test files for context/import style
    existing_test_content = ""
    for tf in state.get("test_files", [])[:2]:
        try:
            with open(os.path.join(base_path, tf), "r", encoding="utf-8", errors="ignore") as f:
                existing_test_content += f"\n\n# Existing test: {tf}\n" + f.read()[:2000]
        except:
            pass

    prompt = PromptTemplate.from_template("""
    You are a senior software engineer writing pytest tests.
    
    Bug: {title}
    Description: {body}
    Fix Applied: {fix_plan}
    
    Existing test style for reference:
    {existing_tests}
    
    Write 3 new pytest test cases:
    1. A test that reproduces the original bug (should fail before fix, pass after)
    2. A test for the happy path (valid input)
    3. An edge case test
    
    Use the same import style as the existing tests.
    Return ONLY raw Python code, no markdown, no backticks.
    """)

    chain = prompt | llm
    result = chain.invoke({
        "title": state["issue_title"],
        "body": state["issue_body"],
        "fix_plan": state.get("fix_plan", ""),
        "existing_tests": existing_test_content or "# No existing tests found"
    })

    generated_tests = result.content.strip()
    if generated_tests.startswith("```"):
        lines = generated_tests.split("\n")
        generated_tests = "\n".join(lines[1:-1])

    # Decide where to write the test file
    if state.get("test_files"):
        # Append to the first existing test file
        test_file_path = state["test_files"][0]
    else:
        test_file_path = "tests/test_ai_generated.py"
        os.makedirs(os.path.join(base_path, "tests"), exist_ok=True)

    logs.append(f"🧪 [Test Generator] Generated 3 test cases for '{test_file_path}'")

    return {
        **state,
        "generated_tests": generated_tests,
        "test_file_path": test_file_path,
        "logs": logs,
        "current_node": "test_generator",
    }
