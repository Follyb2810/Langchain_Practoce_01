from langchain_core.tools import tool

@tool
def get_user_profile(user_id: str) -> dict:
    """Fetch user profile (id + name)."""
    # TODO: Replace with real DB lookup
    try:
        return {"id": user_id, "name": "John Doe"}
    except Exception:
        # fallback
        return {"id": user_id, "name": "Guest"}
