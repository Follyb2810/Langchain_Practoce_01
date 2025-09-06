"""
Example: Using Different Memory Classes in LangChain
====================================================

This script shows how to use different memory classes in LangChain.
Each memory type has trade-offs depending on your use case:
    - Do you want to keep *all* history?
    - Do you want to keep only the *last N messages*?
    - Do you want to *summarize* to save space?
    - Do you want to *save to disk* for persistence?
"""

from langchain_core.memory import BaseMemory
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory,
    FileChatMessageHistory,
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ----------------------------------------------------
# 1. BaseMemory → Abstract class for building custom memory
# ----------------------------------------------------
# BaseMemory is not used directly, but you can subclass it
# if you want to design your own memory system (e.g., saving
# messages in Redis, MongoDB, or a custom vector store).
class MyCustomMemory(BaseMemory):
    def __init__(self):
        self.store = []

    def load_memory_variables(self, inputs):
        """Return all memory as a dictionary."""
        return {"history": self.store}

    def save_context(self, inputs, outputs):
        """Save new interactions into memory."""
        self.store.append((inputs, outputs))

    def clear(self):
        """Clear memory store."""
        self.store = []


# ----------------------------------------------------
# 2. ConversationBufferMemory → Keep *all* conversation history
# ----------------------------------------------------
# Good when your conversations are short and you want the model
# to always see the full history.
buffer_memory = ConversationBufferMemory(return_messages=True)
buffer_memory.chat_memory.add_message(HumanMessage(content="Hi!"))
buffer_memory.chat_memory.add_message(AIMessage(content="Hello, how can I help?"))

print("\n--- ConversationBufferMemory ---")
print(buffer_memory.load_memory_variables({}))


# ----------------------------------------------------
# 3. ConversationBufferWindowMemory → Keep *only the last N messages*
# ----------------------------------------------------
# Useful when you want to avoid sending a huge context to the LLM.
# Example: keep only the last 2 exchanges.
window_memory = ConversationBufferWindowMemory(k=2, return_messages=True)
for i in range(5):
    window_memory.chat_memory.add_message(HumanMessage(content=f"User says {i}"))
    window_memory.chat_memory.add_message(AIMessage(content=f"Bot replies {i}"))

print("\n--- ConversationBufferWindowMemory (last 2 exchanges) ---")
print(window_memory.load_memory_variables({}))


# ----------------------------------------------------
# 4. ConversationSummaryMemory → Summarize the conversation
# ----------------------------------------------------
# Instead of keeping all messages, this uses an LLM to summarize
# the history into a shorter form. This is ideal for long conversations
# where you don’t want to blow up the context window.
# (Here we use a fake summarizer for demo purposes.)
class FakeSummarizer:
    def predict(self, text):
        return "This is a short summary of the conversation."


summary_memory = ConversationSummaryMemory(llm=FakeSummarizer(), return_messages=True)
summary_memory.chat_memory.add_message(
    HumanMessage(content="Tell me about space travel.")
)
summary_memory.chat_memory.add_message(
    AIMessage(content="Space travel is the journey beyond Earth’s atmosphere.")
)

print("\n--- ConversationSummaryMemory ---")
print(summary_memory.load_memory_variables({}))


# ----------------------------------------------------
# 5. ConversationSummaryBufferMemory → Mix of buffer + summary
# ----------------------------------------------------
# It keeps a rolling buffer of the last N messages + a summary of older ones.
# Best when you need some recent detail but don’t want to store everything.
summary_buffer_memory = ConversationSummaryBufferMemory(
    llm=FakeSummarizer(),
    max_token_limit=50,  # After this limit, older messages get summarized
    return_messages=True,
)
summary_buffer_memory.chat_memory.add_message(
    HumanMessage(content="User: Start conversation")
)
summary_buffer_memory.chat_memory.add_message(AIMessage(content="Bot: Ok, let’s talk."))

print("\n--- ConversationSummaryBufferMemory ---")
print(summary_buffer_memory.load_memory_variables({}))


# ----------------------------------------------------
# 6. FileChatMessageHistory → Persistent storage on disk
# ----------------------------------------------------
# Useful when you want conversations to be saved between sessions.
# Messages are written to a local file.
file_history = FileChatMessageHistory("chat_history.json")
file_history.add_message(HumanMessage(content="Persist this message!"))
file_history.add_message(AIMessage(content="I will remember this next time."))

print("\n--- FileChatMessageHistory (saved to disk) ---")
print(file_history.messages)


# ----------------------------------------------------
# Summary: When to Use Which
# ----------------------------------------------------
"""
✅ ConversationBufferMemory
    - Keeps all messages
    - Best for short chats where full history is important
    - Risk: context can grow too large

✅ ConversationBufferWindowMemory
    - Keeps only last N exchanges
    - Best for long chats when only recent context matters
    - Risk: older context is lost

✅ ConversationSummaryMemory
    - Summarizes old history into short text
    - Best for very long chats (scalable memory)
    - Risk: summaries might lose fine details

✅ ConversationSummaryBufferMemory
    - Hybrid (summary + last few messages)
    - Best trade-off between detail and scalability

✅ FileChatMessageHistory
    - Persists chat to disk (or load back later)
    - Best when you want state across multiple runs
    - Risk: file size grows if not managed

✅ BaseMemory
    - Abstract class for building your own custom memory system
    - Best when integrating with external DBs or vector stores
"""
