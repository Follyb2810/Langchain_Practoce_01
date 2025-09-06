# -------------------------
# Import required libraries
# -------------------------
import os

# LangChain hub for prompts
from langchain import hub
# Agent framework
from langchain.agents import AgentExecutor, create_react_agent
# RAG chains
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# Vector store (Chroma)
from langchain_community.vectorstores import Chroma
# Messages (chat history)
from langchain_core.messages import AIMessage, HumanMessage
# Prompt templates
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# Tool wrapper
from langchain_core.tools import Tool
# Ollama LLM for local inference
from langchain_ollama import ChatOllama
# Local HuggingFace embeddings (Xenova models run in pure Python)
from langchain_community.embeddings import HuggingFaceEmbeddings


# -------------------------
# Load Chroma Vector Store
# -------------------------
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
# Example: use sentence-transformers all-MiniLM (small, fast)
# You can replace with any other HF model supported by Xenova
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma with local embeddings
db = Chroma(persist_directory=persistent_directory,
            embedding_function=embeddings)

# -------------------------
# Create Retriever
# -------------------------
retriever = db.as_retriever(
    search_type="similarity",   # similarity search
    search_kwargs={"k": 3},     # return top 3 docs
)

# -------------------------
# Local LLM (Ollama)
# -------------------------
# Make sure Ollama is running locally: `ollama run mistral` or similar
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
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Reformulate history-aware questions
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
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# -------------------------
# Build Retrieval QA Chain
# -------------------------
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(
    history_aware_retriever, question_answer_chain
)

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
    handle_parsing_errors=True,
    verbose=True,
)

# -------------------------
# Chat Loop
# -------------------------
chat_history = []
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break

    response = agent_executor.invoke(
        {"input": query, "chat_history": chat_history}
    )
    print(f"AI: {response['output']}")

    # Update history for next round
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response["output"]))
