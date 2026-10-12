import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage

load_dotenv()

DEMO_MODE = not os.getenv("GEMINI_API_KEY", "").startswith("AIzaSy")

def _mock_fn(prompt_value) -> AIMessage:
    """
    Receives a PromptValue from the prompt template
    and returns a realistic mock AI response based on keywords.
    """
    # PromptTemplate outputs a StringPromptValue — convert to plain text safely
    if hasattr(prompt_value, 'to_string'):
        text = prompt_value.to_string().lower()
    elif hasattr(prompt_value, 'text'):
        text = prompt_value.text.lower()
    else:
        text = str(prompt_value).lower()

    if "classify" in text or "bug type" in text or "category" in text:
        return AIMessage(content="validation")

    if "file paths" in text or "which files" in text or "json list" in text:
        return AIMessage(content='["app.py", "routes.py", "models.py"]')

    if "confidence" in text or "specific function" in text or "json" in text and "functions" in text:
        return AIMessage(content='{"functions": ["search", "get_results"], "confidence": 0.87, "reasoning": "The search function does not handle empty string input, causing an unhandled exception when passed to the database."}')

    if "fix plan" in text or "proposed fix" in text or "no code yet" in text:
        return AIMessage(content="""**Root Cause:** The search function passes the raw query directly to the database without validating for empty or null values.

**Proposed Fix:**
- Add a guard clause at the top of the search function
- Return an empty list [] when query is blank or whitespace-only
- Add HTTP 422 for completely null inputs

**Files to Modify:**
- routes.py — add guard clause before calling search
- models.py — add validation in query builder

**New Tests Needed:**
- test_search_with_empty_string
- test_search_with_whitespace
- test_search_with_valid_query""")

    if "fixed version" in text or "complete fixed" in text or "bug fixed" in text or "fix" in text and "file" in text:
        return AIMessage(content="""def search(query: str):
    # FIX: Validate empty input before querying the database
    if not query or not query.strip():
        return []
    return db.execute(query.strip())
""")

    if "pytest" in text or "test cases" in text or "3 new" in text:
        return AIMessage(content="""import pytest

def test_search_empty_string():
    result = search("")
    assert result == []

def test_search_whitespace_only():
    result = search("   ")
    assert result == []

def test_search_valid_query():
    result = search("hello")
    assert isinstance(result, list)
""")

    if "pull request" in text or "pr description" in text or "root cause" in text and "files changed" in text:
        return AIMessage(content="""## 🤖 Root Cause
The search endpoint passed raw query strings to the database without validating for empty values.

## ✅ Fix Applied
Added input validation in routes.py to return an empty list when query is blank.

## 🧪 Tests
✅ 3 new AI-generated tests added and passing.

## 📁 Files Changed
- routes.py (+5 lines, -1 line)
- tests/test_search.py (+18 lines)""")

    return AIMessage(content="validation")


def get_llm(model: str = "gemini-2.0-flash"):
    """
    Returns a real Gemini LLM, or a RunnableLambda mock in demo mode.
    RunnableLambda is fully compatible with LangChain's | pipe operator.
    """
    if DEMO_MODE:
        print("⚠️  DEMO MODE: No valid Gemini API key found. Using mock LLM.")
        return RunnableLambda(_mock_fn)

    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0.1,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
