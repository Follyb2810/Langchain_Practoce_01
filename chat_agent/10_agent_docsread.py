import os

# Import LangChain hub for pulling prebuilt prompts
from langchain import hub

# AgentExecutor runs agents, create_react_agent builds a ReAct-style agent
from langchain.agents import AgentExecutor, create_react_agent

# Chains for retrieval-augmented generation (RAG)
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Chroma vector DB for embeddings
from langchain_community.vectorstores import Chroma

# Message objects for chat history
from langchain_core.messages import AIMessage, HumanMessage

# Templates for building chat prompts
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Wrapper for tools that agents can call
from langchain_core.tools import Tool

# OpenAI models (chat + embeddings)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# -------------------------
# Load Chroma Vector Store
# -------------------------
# Get current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Path to your vector DB (stored in a rag project folder)
db_dir = os.path.join(current_dir, "..", "..", "4_rag", "db")
# The folder where Chroma persisted the embeddings
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")

# Check if the vector DB exists; if not, raise an error
if os.path.exists(persistent_directory):
    print("Loading existing vector store...")
    db = Chroma(persist_directory=persistent_directory, embedding_function=None)
else:
    raise FileNotFoundError(
        f"The directory {persistent_directory} does not exist. Please check the path."
    )

# -------------------------
# Define Embeddings
# -------------------------
# OpenAI embeddings (can be swapped with local ones if needed)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Reload vector store with embeddings so it knows how to query vectors
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# -------------------------
# Create Retriever
# -------------------------
# Retriever abstracts DB lookup; lets us query top k documents
retriever = db.as_retriever(
    search_type="similarity",  # Use similarity search
    search_kwargs={"k": 3},  # Return top 3 results
)

# -------------------------
# Create LLM
# -------------------------
# ChatOpenAI wraps OpenAI chat models
llm = ChatOpenAI(model="gpt-4o")

# -------------------------
# Contextualization Prompt
# -------------------------
# This ensures that when a user asks "What about him?" the model
# rewrites it into a standalone question ("What about Einstein?")
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, just "
    "reformulate it if needed and otherwise return it as is."
)

# Prompt template for contextualizing questions
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),  # Instructions for the model
        MessagesPlaceholder("chat_history"),  # Where chat history is injected
        ("human", "{input}"),  # Latest user input
    ]
)

# History-aware retriever reformulates user queries before retrieving
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# -------------------------
# Answering Prompt
# -------------------------
# Instruction prompt for concise answers using retrieved docs
qa_system_prompt = (
    "You are an assistant for question-answering tasks. Use "
    "the following pieces of retrieved context to answer the "
    "question. If you don't know the answer, just say that you "
    "don't know. Use three sentences maximum and keep the answer "
    "concise."
    "\n\n"
    "{context}"  # Inject retrieved context here
)

# Prompt template for Q&A
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),  # Instructions + context
        MessagesPlaceholder("chat_history"),  # Preserve conversation flow
        ("human", "{input}"),  # New user query
    ]
)

# -------------------------
# Build Retrieval QA Chain
# -------------------------
# Stuffing chain → dump all retrieved docs into prompt
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Retrieval chain = (reformulate question if needed) → retrieve docs → answer
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# -------------------------
# Tools for ReAct Agent
# -------------------------
# Pull the ReAct agent prompt (how it reasons and acts)
react_docstore_prompt = hub.pull("hwchase17/react")

# Define a tool that wraps our RAG pipeline
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
# ReAct agent = LLM + Tools + Prompt (it decides when to call tools)
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_docstore_prompt,
)

# Wrap into an executor that handles tool calls and model outputs
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,  # Avoid crashing if output isn't perfectly formatted
    verbose=True,  # Print reasoning steps
)

# -------------------------
# Chat Loop
# -------------------------
chat_history = []  # Store conversation
while True:
    query = input("You: ")  # Take user input
    if query.lower() == "exit":  # Exit condition
        break

    # Invoke the agent with query + conversation history
    response = agent_executor.invoke({"input": query, "chat_history": chat_history})
    print(f"AI: {response['output']}")

    # Save messages into chat history for context in next round
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response["output"]))
