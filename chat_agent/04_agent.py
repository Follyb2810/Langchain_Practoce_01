# -------------------------
# Imports
# -------------------------
from datetime import datetime
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain.agents import (
    create_tool_calling_agent,   # structured tool-calling agent
    AgentExecutor,
)


# -------------------------
# Define a tool (plain Python function wrapped as a LangChain Tool)
# -------------------------
def get_current_time():
    """Return the current system time as a string"""
    current_time = datetime.now()
    return current_time.strftime("%I:%M %p")

# Wrap the function as a LangChain Tool object
tools = [
    Tool(
        name="Time",                               # name the LLM will use
        func=get_current_time,                     # Python function to execute
        description="Useful for when you need to know the current time",  # helps LLM decide when to use
    )
]


# -------------------------
# Define the LLM
# -------------------------
# This example uses Ollama with the "mistral" model.
# You need Ollama running locally.
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")


# -------------------------
# Create the agent (function-calling style)
# -------------------------
# - This agent knows how to call tools directly using structured arguments (JSON).
tool_calling_agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
)


# -------------------------
# Option 1: AgentExecutor.from_agent_and_tools (recommended helper)
# -------------------------
tool_executor = AgentExecutor.from_agent_and_tools(
    agent=tool_calling_agent,   # pass in the agent
    tools=tools,                # pass in the list of tools
    verbose=True,               # print reasoning/steps as the agent runs
)

print("---- Running with from_agent_and_tools ----")
response1 = tool_executor.invoke({"input": "What time is it?"})
print("Response (from_agent_and_tools):", response1)


# -------------------------
# Option 2: AgentExecutor(...) direct constructor
# -------------------------
# - This does the same thing, but you call the constructor directly.
# - You have to make sure you pass both the agent and tools correctly.
executor = AgentExecutor(
    agent=tool_calling_agent,   # agent object
    tools=tools,                # tools list
    verbose=True,               # debugging output
)

print("\n---- Running with direct AgentExecutor ----")
response2 = executor.invoke({"input": "What time is it?"})
print("Response (AgentExecutor direct):", response2)


# -------------------------
# Notes
# -------------------------
# Both tool_executor and executor run the same way.
# The only difference is that `.from_agent_and_tools` is a convenience
# classmethod that wires things up for you,
# while the direct constructor gives you full manual control.
