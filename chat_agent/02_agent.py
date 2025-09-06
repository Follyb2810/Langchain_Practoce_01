from langchain_core.tools import tool
from langchain_ollama import ChatOllama



@tool
def get_user_by_id(user_id: int):
    """
    Get user information by ID.
    The argument (user_id: int) tells LangChain this tool
    requires an integer parameter named `user_id`.
    """
    # Simulated database lookup
    users = {
        1: {"name": "Alice", "age": 25},
        2: {"name": "Bob", "age": 30},
    }

    # Return the user if found, otherwise return an error message
    return users.get(user_id, {"error": "User not found"})


# -------------------------
# Another tool with multiple arguments
# -------------------------

@tool
def update_user_profile(user_id: int, location: str, occupation: str):
    """
    Update a user's profile.
    Multiple arguments are supported, and LangChain will
    create a schema for each of them.
    """
    # Example of how you might process the update
    updated_profile = {
        "user_id": user_id,
        "location": location,
        "occupation": occupation,
        "status": "Profile updated successfully"
    }

    return updated_profile


# -------------------------
# Collect tools into a list
# -------------------------
tools = [get_user_by_id, update_user_profile]

# Print the tools
print(tools)

# Example output looks like:
# [
#   StructuredTool(
#       name='get_user_by_id',
#       description='Get user information by ID.',
#       args_schema={'user_id': 'int'}
#   ),
#   StructuredTool(
#       name='update_user_profile',
#       description="Update a user's profile.",
#       args_schema={'user_id': 'int', 'location': 'str', 'occupation': 'str'}
#   )
# ]


# -------------------------
# (Optional) Example usage with an agent
# -------------------------
"""
model = ChatOllama(model="mistral")

from langchain.agents import initialize_agent

# Initialize an agent with tools
agent = initialize_agent(tools, model, agent="zero-shot-react-description", verbose=True)

# The LLM can now decide to call `get_user_by_id(user_id=1)` automatically
response = agent.run("Show me the profile of user with ID 1")
print(response)

# Or it can call `update_user_profile` if needed
response = agent.run("Update user 2's profile to location=London and occupation=Engineer")
print(response)
"""
