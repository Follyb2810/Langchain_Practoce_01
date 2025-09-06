import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings

# Use mistral in Ollama for answering
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "books", "odyssey.txt")
persistent_directory = os.path.join(current_dir, "db", "chromadb")

# ✅ Use CPU-only embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}  # important on Intel Macs
)

if not os.path.exists(persistent_directory):
    print("No vector store found, creating one...")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist")

    loader = TextLoader(file_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    db = Chroma.from_documents(
        docs, embeddings, persist_directory=persistent_directory
    )
    print("✅ Vector store created.")
else:
    db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)
    print("✅ Vector store loaded.")

# 🔎 Test similarity search
query = "Who is Odysseus?"
results = db.similarity_search(query, k=2)

for i, r in enumerate(results, 1):
    print(f"\nResult {i}: {r.page_content[:300]}")
