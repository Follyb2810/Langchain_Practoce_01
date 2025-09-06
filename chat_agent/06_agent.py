from datetime import datetime
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama



llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    now = datetime.now()
    return now.strftime("%I:%M %p")   


def search_wikipedia(query):
    """Searches Wikipedia and returns the summary of the first result."""
    from wikipedia import summary
    try:
        return summary(query, sentences=2)
    except:
        return "I couldn't find any information on that"


tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when we need to know current time",
    ),
    Tool(
        name="Wikipedia",
        func=search_wikipedia,
        description="Useful for when we need to know information about a topic",
    ),
]


prompt = hub.pull("hwchase17/structured-chat-agent")
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)


# ----------------------------
# Manage memories per user
# ----------------------------
# Instead of a single memory, we keep a dictionary:
# user_id -> ConversationBufferMemory
user_memories = {}


def get_memory_for_user(user_id: str) -> ConversationBufferMemory:
    """Return (or create) a ConversationBufferMemory for a given user_id."""
    if user_id not in user_memories:
        # Create a new memory just for this user
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Add an initial system instruction into their memory
        initial_message = (
            "You are an AI assistant that can provide helpful answers using available tools. "
            "If you are unable to answer, you can use the following tools: Time and Wikipedia."
        )
        memory.chat_memory.add_message(SystemMessage(content=initial_message))

        # Save it
        user_memories[user_id] = memory
    return user_memories[user_id]


# ----------------------------
# Main loop (simulate multiple users)
# ----------------------------
while True:
    # Simulate user identification (in a real app, this could come from auth/session)
    user_id = input("\nEnter your user id: ")
    if user_id.lower() in ["exit", "quit"]:
        break

    # Get memory for this specific user
    memory = get_memory_for_user(user_id)

    # Build an executor with user-specific memory
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,   # <-- DIFFERENT for each user
    )

    # Get input from the user
    user_input = input(f"User ({user_id}): ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # Save human message
    memory.chat_memory.add_message(HumanMessage(content=user_input))

    # Run the agent
    response = agent_executor.invoke({"input": user_input})

    # Print and save AI response
    print("Bot:", response["output"])
    memory.chat_memory.add_message(AIMessage(content=response["output"]))
