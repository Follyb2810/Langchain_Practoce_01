from langchain_core.tools import tool

@tool
def check_existing_consultation(user_id: str) -> dict:
    """Check if user has an active consultation."""
    # TODO: Replace with real DB lookup
    try:
        return {"active": False, "doctorId": None, "doctorName": None}
    except Exception:
        # fallback
        return {"active": False, "doctorId": None, "doctorName": None}
