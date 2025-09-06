from langchain_core.tools import tool

@tool
def assign_doctor(user_id: str, role: str) -> dict:
    """Assign the least busy doctor for the given role."""
    # TODO: Replace with DB logic
    try:
        return {"doctorId": "d456", "doctorName": "Dr. Alice"}
    except Exception:
        # fallback
        return {"doctorId": "d000", "doctorName": "On-call Doctor"}
