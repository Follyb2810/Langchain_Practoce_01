import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama import ChatOllama, OllamaEmbeddings  # ✅ use Ollama embeddings

# Initialize LLM
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "books", "odyssey.txt")
persistent_directory = os.path.join(current_dir, "db", "chromadb")

# Initialize embeddings (local)
embeddings = OllamaEmbeddings(model="mistral")  # or "nomic-embed-text" if you have it

# If no existing vector store, build it
if not os.path.exists(persistent_directory):
    print("No vector store found, creating one...")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist")

    # Load the text
    loader = TextLoader(file_path)
    documents = loader.load()

    # Split into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    print("\n--- Creating vector store ---")
    db = Chroma.from_documents(
        docs, embeddings, persist_directory=persistent_directory
    )
    print("\n--- Finished creating vector store ---")

else:
    print("Vector store already exists. Loading it...")
    db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# ✅ Test query
query = "Who is Odysseus?"
results = db.similarity_search(query, k=3)
for i, r in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(r.page_content[:300])
