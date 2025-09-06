from langchain_core.tools import tool
from langchain_ollama import ChatOllama


@tool
def get_user_id():
    """
    return user id
    (The docstring is used as the tool description for the LLM)
    """
    # Returning a dictionary with a key-value pair
    # IMPORTANT: {"id"} would be a set, not a dict
    return {"id": 123}


@tool
def get_user_name():
    """
    return user name
    """
    return {"name": "Alice"}


@tool
def get_user_profile():
    """
    return user profile
    """
    return {"profile": {"age": 25, "location": "NYC"}}



tools = [get_user_id, get_user_name, get_user_profile]

print(tools)

# Example output will look like:
# [
#   StructuredTool(name='get_user_id', description='return user id', ...),
#   StructuredTool(name='get_user_name', description='return user name', ...),
#   StructuredTool(name='get_user_profile', description='return user profile', ...)
# ]


# Example: create an Ollama LLM agent that can call these tools
# (this requires you to have Ollama running locally)
"""
model = ChatOllama(model="mistral")

# You could then pass these tools to an agent like so:
from langchain.agents import initialize_agent

agent = initialize_agent(tools, model, agent="zero-shot-react-description", verbose=True)

# Ask the agent a question — it will decide when to call your tools
response = agent.run("What is the user's profile?")
print(response)
"""
