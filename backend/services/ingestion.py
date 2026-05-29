from langchain_community.document_loaders import GithubFileLoader
from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import os
from database.vectorstore import store_embeddings_supabase, supabase
from services.models import Models
# from supabase import create_client
load_dotenv()

EXT_TO_LANGUAGE = {
    ".py": Language.PYTHON,
    ".js": Language.JS, ".ts": Language.JS,
    ".jsx": Language.JS, ".tsx": Language.JS,
    ".html": Language.HTML,
    ".md": Language.MARKDOWN,
}

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c",
    ".html", ".css", ".json", ".yaml", ".yml", ".md", ".txt", ".ipynb"
}
IGNORED_DIRS = {"migrations", "alembic", "node_modules", "dist", "build", ".vite"}
IGNORED_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "vite.config.js",
    "vite.config.ts", "eslint.config.js", "package.json", "tsconfig.json",
    "webpack.config.js", "babel.config.js", "components.json", "config.js",
    ".config.js", "jsconfig.json"
}

# ── Single shared embeddings instance (avoids re-init overhead per call) ──────
# @lru_cache(maxsize=1)
# def get_embeddings() -> OllamaEmbeddings:
#     return OllamaEmbeddings(model="embeddinggemma")


def should_load(path: str) -> bool:
    parts = path.split("/")
    if set(parts) & IGNORED_DIRS:
        return False
    if path.split("/")[-1] in IGNORED_FILES:
        return False
    return any(path.endswith(ext) for ext in ALLOWED_EXTENSIONS)


def _collection_exists(repo_name: str) -> bool:
    """Check if a Chroma collection already exists for this repo."""
    collection_name = repo_name.replace("/", "_")
    return supabase.table("documents").select("*").eq("source", collection_name).execute().data

    # client = chromadb.PersistentClient(persistent_directory)
    # return collection_name in [c.name for c in client.list_collections()]


def _fetch_file(loader: GithubFileLoader, file: dict, repo_name: str) -> Document | None:
    """Fetch a single file — designed to be called concurrently."""
    path = file["path"]
    try:
        content = loader.get_file_content_by_path(path)
    except Exception as e:
        print(f"[Warning] skipping {path}: {e}")
        return None

    if not content:
        return None

    ext = os.path.splitext(path)[1]
    return Document(
        page_content=content,
        metadata={"source": path, "repo": repo_name, "Language": ext.lstrip(".")},
    )


def load_documents(repo_name: str, max_workers: int = 10) -> list[Document]:
    """
    Load all repo files in parallel using a thread pool.
    max_workers=10 is a safe default — GitHub allows ~5k requests/hour
    unauthenticated; authenticated is much higher.
    """
    loader = GithubFileLoader(
        repo=repo_name,
        branch="main",
        access_token=os.getenv("ACCESS_TOKEN"),
        github_api_url="https://api.github.com",
        file_filter=should_load,
    )

    paths = loader.get_file_paths()
    documents: list[Document] = []

    # Parallel HTTP fetches — the original was fully sequential
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_file, loader, f, repo_name): f for f in paths}
        for future in as_completed(futures):
            doc = future.result()
            if doc:
                print(f"Loaded: {doc.metadata['source']}")
                documents.append(doc)

    return documents


def _chunk_document(doc: Document, chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Chunk a single document — designed to be called concurrently."""
    ext = "." + doc.metadata.get("Language", "text").lower()
    lang = EXT_TO_LANGUAGE.get(ext)

    if lang:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=lang,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    return splitter.split_documents([doc])


def chunking_documents(
    documents: list[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    max_workers: int = 4,
) -> list[Document]:
    """
    Chunk all documents in parallel.
    CPU-bound so max_workers stays low (4) — matches typical core count
    without over-subscribing the GIL.
    """
    all_chunks: list[Document] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_chunk_document, doc, chunk_size, chunk_overlap)
            for doc in documents
        ]
        for future in as_completed(futures):
            all_chunks.extend(future.result())

    print(f"Chunking completed. Total chunks: {len(all_chunks)}")
    return all_chunks


# def create_vector_collection(
#     repo_name: str,
#     chunks: list[Document],
#     persistent_directory: str = "db/chroma_db",
#     batch_size: int = 100,
# ) -> Chroma:
#     """
#     Embed and store chunks in Chroma in controlled batches.
#     batch_size=100 prevents OOM on large repos — Ollama processes
#     at most 100 chunks at a time instead of all at once.
#     """
#     embeddings = get_embeddings()
#     collection_name = repo_name.replace("/", "_")

#     # Batch-add documents to prevent memory spikes
#     vector_store = None
#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i : i + batch_size]
#         print(f"Embedding batch {i // batch_size + 1} / {-(-len(chunks) // batch_size)}")

#         if vector_store is None:
#             vector_store = Chroma.from_documents(
#                 documents=batch,
#                 embedding=embeddings,
#                 persist_directory=persistent_directory,
#                 collection_name=collection_name,
#                 collection_metadata={"hnsw:space": "cosine"},
#             )
#         else:
#             vector_store.add_documents(batch)

#     print(f"Created vector collection for {repo_name} successfully.")
#     return vector_store


def ingest_pipeline(
    url: str,
    force: bool = False,
):
    """
    Full ingestion pipeline with an early-exit guard.

    Args:
        url:                  GitHub repo in "owner/repo" format.
        persistent_directory: Chroma storage path.
        force:                Re-ingest even if the collection already exists.
    """
    # ── Early exit: skip load + chunk + embed if already ingested ─────────────
    if not force and _collection_exists(url):
        print(f"Collection for {url} already exists. Pass force=True to re-ingest.")
        return {"message": f"Collection for {url} already exists. Ingestion skipped."}

    docs = load_documents(url)
    chunks = chunking_documents(docs)
    store_embeddings_supabase(url, chunks)

    return {"message": f"Ingestion completed for {url}. Total chunks: {len(chunks)}"}