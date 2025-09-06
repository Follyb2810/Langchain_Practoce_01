from langchain_core.tools import tool, Tool
from datetime import datetime
from langchain.agents import (
    create_react_agent,           # ReAct-style agent (Reason + Act loop)
    create_tool_calling_agent,    # OpenAI function-calling style agent
    AgentExecutor,
)
from langchain import hub
from langchain_ollama import ChatOllama


llm = ChatOllama(model="mistral", base_url="http://localhost:11434")


def get_current_time():
    """Return the current system time as a string"""
    current_time = datetime.now()
    return current_time.strftime("%I:%M %p")

tools = [
    Tool(
        name="Time",                               # tool name
        func=get_current_time,                     # Python function to call
        description="Useful for when you need to know the current time",
    )
]


# -------------------------
# Option 1: ReAct Agent (Reason + Act loop)
# -------------------------
# - ReAct = "Reasoning + Acting"
# - The agent *thinks step by step* ("Thought") and decides what tool to call ("Action").
# - This style was the original LangChain agent framework.
# - It uses a custom prompt (from the LangChain hub).
prompt = hub.pull("hwchase17/react")

react_agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,          # ReAct prompt instructs LLM how to reason + act
    stop_sequence=True,     # tells LLM when to stop tool-calling
)

# Executor: runs the agent and tools together
react_executor = AgentExecutor.from_agent_and_tools(
    agent=react_agent,
    tools=tools,
    verbose=True,
)

print("---- ReAct Agent ----")
response_react = react_executor.invoke({"input": "What time is it?"})
print("ReAct Response:", response_react)


# -------------------------
# Option 2: Tool-Calling Agent (function calling style)
# -------------------------
# - Uses the new "function calling" paradigm popularized by OpenAI.
# - Instead of prompting "Reason + Act" in text, the LLM is asked to directly
#   output JSON describing the tool call.
# - Cleaner, less prompt-engineering, more structured.
# - Works great with models that support structured tool calling (e.g., OpenAI, some Ollama builds).
tool_calling_agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
)

tool_executor = AgentExecutor.from_agent_and_tools(
    agent=tool_calling_agent,
    tools=tools,
    verbose=True,
)

print("---- Tool-Calling Agent ----")
response_tool_call = tool_executor.invoke({"input": "What time is it?"})
print("Tool-Calling Response:", response_tool_call)
