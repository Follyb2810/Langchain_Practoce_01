import os

# LangChain hub for prebuilt prompts
from langchain import hub

# Agent framework
from langchain.agents import AgentExecutor, create_react_agent,create_tool_calling_agent

# Retrieval-augmented generation (RAG) utilities
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

# Vector store (Chroma for local persistence)
from langchain_community.vectorstores import Chroma

# Chat message objects for history
from langchain_core.messages import AIMessage, HumanMessage

# Prompt templates
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Tool wrapper so agents can call functions
from langchain_core.tools import Tool

# Ollama LLM for local models
from langchain_ollama import ChatOllama

# Local embeddings (Xenova HuggingFace models)
from langchain_community.embeddings import HuggingFaceEmbeddings

current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "..", "..", "4_rag", "db")
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")

if not os.path.exists(persistent_directory):
    raise FileNotFoundError(
        f"The directory {persistent_directory} does not exist. Please check the path."
    )

print("Loading existing vector store...")

# -------------------------
# Define Local Embeddings
# -------------------------
# Example: use MiniLM — small, fast, and works offline
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma DB with local embeddings
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# -------------------------
# Create Retriever
# -------------------------
retriever = db.as_retriever(
    search_type="similarity",  # Use similarity search
    search_kwargs={"k": 3},  # Return top 3 results
)

# -------------------------
# Local LLM (Ollama)
# -------------------------
# Make sure Ollama is running: e.g. `ollama run mistral`
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# -------------------------
# Contextualization Prompt
# -------------------------
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, just "
    "reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),  # Instructions
        MessagesPlaceholder("chat_history"),  # Chat history goes here
        ("human", "{input}"),  # Latest user query
    ]
)

# Reformulate queries based on history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# -------------------------
# QA Prompt
# -------------------------
qa_system_prompt = (
    "You are an assistant for question-answering tasks. Use "
    "the following pieces of retrieved context to answer the "
    "question. If you don't know the answer, just say that you "
    "don't know. Use three sentences maximum and keep the answer "
    "concise."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),  # System instructions
        MessagesPlaceholder("chat_history"),  # Inject conversation history
        ("human", "{input}"),  # New query
    ]
)

# -------------------------
# Build Retrieval QA Chain
# -------------------------
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# -------------------------
# Tools for ReAct Agent
# -------------------------
react_docstore_prompt = hub.pull("hwchase17/react")

tools = [
    Tool(
        name="Answer Question",
        func=lambda input, **kwargs: rag_chain.invoke(
            {"input": input, "chat_history": kwargs.get("chat_history", [])}
        ),
        description="Useful for answering questions about the context using retrieved documents.",
    )
]

# -------------------------
# Build ReAct Agent
# -------------------------
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_docstore_prompt,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,  # Prevents crashes if output is malformed
    verbose=True,  # Debug: show reasoning steps
)

# -------------------------
# Chat Loop
# -------------------------
chat_history = []  # Keep track of user/AI messages
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break

    response = agent_executor.invoke({"input": query, "chat_history": chat_history})
    print(f"AI: {response['output']}")

    # Save messages to history
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response["output"]))
