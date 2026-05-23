from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import chromadb
from langchain_core.documents import Document

chunks = [
    Document(
        page_content="Authentication is handled in auth.py using JWT tokens.",
        metadata={"file": "auth.py"}
    ),
    Document(
        page_content="The database connection is initialized in db.py using PostgreSQL.",
        metadata={"file": "db.py"}
    ),
    Document(
        page_content="API routes are defined in routes.py using FastAPI.",
        metadata={"file": "routes.py"}
    ),
]


def create_vector_collection(repo_name: str, chunks: list, persistent_directory: str = "db/chroma_db") -> None:
    """This function creates a vector collection from the chunks."""
    
    embeddings = OllamaEmbeddings(model="embeddinggemma")
    collection_name = repo_name.replace("/", "_")

    client = chromadb.PersistentClient(path=persistent_directory)
    existing = [c.name for c in client.list_collections()]
    print("Existing Collections:", existing)

    if collection_name in existing:
        print(f"Vector Collection for {repo_name} already exists. Skipping creation.")
        return Chroma(
            embedding_function=embeddings,
            persist_directory=persistent_directory,
            collection_name=collection_name,
        )
    
    
    vector_store = Chroma.from_documents(
        embedding=embeddings,
        documents=chunks,
        persist_directory=persistent_directory,
        collection_name=collection_name,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"Created Vector Collection for {repo_name} Successfully!")

    # 🔹 Query test
    retriever = vector_store.as_retriever()

    query = "Where is authentication handled?"
    docs = retriever.invoke(query)

    print("\n🔍 Query:", query)
    print("📄 Results:")
    for d in docs:
        print("-", d.page_content)

    return vector_store


if __name__ == "__main__":
    repo_name = "test_repo"
    create_vector_collection(repo_name, chunks)
    