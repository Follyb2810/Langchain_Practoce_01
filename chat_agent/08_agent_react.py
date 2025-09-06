from datetime import datetime
from langchain import hub
from langchain.agents import (
    create_react_agent,
    create_structured_chat_agent,
    AgentExecutor,
)
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama


# Define a simple tool
def get_current_time():
    now = datetime.now()
    return now.strftime("%I:%M %p")


tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful when you need to know the current time",
    )
]

# Define LLM (Ollama must be running locally with Mistral model)
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

#! Pull the standard ReAct prompt from LangChain Hub
"""
? Why use ReAct?
? Agent will “think out loud”:
? Thought: I need the time → Action: use Time tool → Observation: 3:30 PM → Answer: It’s 3:30 PM
? Great when the LLM must decide between multiple tools with reasoning steps.
! When you want step-by-step reasoning with tool use
"""
prompt = hub.pull("hwchase17/react")

# Create ReAct agent
react_agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Attach to executor
react_executor = AgentExecutor.from_agent_and_tools(
    agent=react_agent, tools=tools, verbose=True
)

# Run query
response = react_executor.invoke({"input": "What time is it right now?"})
print("ReAct Response:", response)

#! Pull structured chat prompt
"""
? LLM doesn’t produce “thinking” text.
? Calls tools in clean JSON format:
? {"action": "Time", "action_input": ""}
?Better when you integrate with systems that need clean tool usage (e.g., APIs, databases).
! When you want clean, API-style tool calls (no messy reasoning in output)
"""
prompt = hub.pull("hwchase17/structured-chat-agent")

# Create Structured Chat agent
structured_agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

# Attach to executor
structured_executor = AgentExecutor.from_agent_and_tools(
    agent=structured_agent, tools=tools, verbose=True
)

# Run query
response = structured_executor.invoke({"input": "What time is it right now?"})
print("Structured Response:", response)


from langchain.prompts import PromptTemplate

#! Custom system instructions
"""

! When you need domain-specific rules or restrictions
"""
custom_prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Only use the Time tool if the user asks about time. "
    "Otherwise, politely say you don’t know.\n\n"
    "Conversation:\n{input}\n\n"
    "Your answer:"
)

# Build agent manually
custom_agent = create_react_agent(llm=llm, tools=tools, prompt=custom_prompt)

custom_executor = AgentExecutor.from_agent_and_tools(
    agent=custom_agent, tools=tools, verbose=True
)

response = custom_executor.invoke({"input": "What time is it?"})
print("Custom Response:", response)

response2 = custom_executor.invoke({"input": "Who is the president of France?"})
print("Custom Response:", response2)
