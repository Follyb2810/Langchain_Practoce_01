from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

# Create a memory store
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Max number of messages to keep
MAX_MESSAGES = 10


def add_message(memory, message):
    """Add a message and trim history to last MAX_MESSAGES."""
    memory.chat_memory.add_message(message)

    # Trim history if too long
    if len(memory.chat_memory.messages) > MAX_MESSAGES:
        memory.chat_memory.messages = memory.chat_memory.messages[-MAX_MESSAGES:]


# ------------------------
# Example usage
# ------------------------
add_message(memory, HumanMessage(content="Hello!"))
add_message(memory, AIMessage(content="Hi there!"))
add_message(memory, HumanMessage(content="What's the time?"))
add_message(memory, AIMessage(content="It's 10:30 AM."))
# ... keep adding messages

print("Current history:", memory.chat_memory.messages)


MAX_MESSAGES = 10


def save_chat_to_db(user_id, new_message, db):
    # Fetch current history from DB
    doc = db.conversations.find_one({"user_id": user_id}) or {"messages": []}
    messages = doc["messages"]

    # Add new message
    messages.append(new_message)

    # Trim to last MAX_MESSAGES
    messages = messages[-MAX_MESSAGES:]

    # Save back
    db.conversations.update_one(
        {"user_id": user_id}, {"$set": {"messages": messages}}, upsert=True
    )
