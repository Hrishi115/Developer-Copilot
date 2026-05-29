from supabase import create_client
import os 
from dotenv import load_dotenv
load_dotenv()
from services.models import Models
from langchain_core.documents import Document

supabase = create_client(
    os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

def store_embeddings_supabase(
    repo_name: str,
    chunks: list[Document],
    batch_size: int = 100,
):
    """
    Embed and store chunks in Supabase in controlled batches.
    batch_size=100 prevents OOM on large repos — Ollama processes
    at most 100 chunks at a time instead of all at once.
    """
    collection_name = repo_name.replace("/", "_")

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f"Embedding batch {i // batch_size + 1} / {-(-len(chunks) // batch_size)}")

        rows = []
        texts = [doc.page_content for doc in batch]
        embeddings = Models.embedding_model(texts)

        for doc, embedding in zip(batch, embeddings):
            text = doc.page_content
            metadata = doc.metadata

            rows.append({
                "content": text,
                "embedding": embedding,
                "source": collection_name,
                "file_path": metadata.get("source"),
            }) 
        supabase.table("documents").insert(rows).execute()

    print(f"Created vector collection for {repo_name} successfully.")


if __name__ == "__main__":
    # Example usage
    chunks = [
        {"page_content": "This is the first document."},
        {"page_content": "This is the second document."},
        # Add more documents as needed
    ]
    store_embeddings_supabase("owner/repo", chunks)