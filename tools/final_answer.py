from langchain_core.tools import tool

@tool
def final_answer(answer: str, result: dict) -> dict:
    """Provide the final structured answer to the user."""
    try:
        return {"answer": answer, "result": result}
    except Exception:
        return {"answer": "Something went wrong.", "result": {}}
