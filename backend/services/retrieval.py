from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

# ── Shared instances (created once per process, not per call) ─────────────────

@lru_cache(maxsize=1)
def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model="embeddinggemma")

@lru_cache(maxsize=1)
def get_model() -> ChatOllama:
    return ChatOllama(model="minimax-m2.5:cloud")

@lru_cache(maxsize=16)
def get_vectorstore(repo_name: str, persistent_directory: str = "db/chroma_db") -> Chroma:
    """
    Cache open Chroma collections by repo name.
    maxsize=16 covers 16 different repos before evicting the oldest —
    fine for MVP with 20-30 devs testing a handful of repos.
    """
    return Chroma(
        embedding_function=get_embeddings(),
        persist_directory=persistent_directory,
        collection_name=repo_name.replace("/", "_"),
    )

# ── System prompt (defined once, not rebuilt on every call) ───────────────────

SYSTEM_MESSAGE = SystemMessage(
    content=(
        "You are a helpful assistant for software developers. "
        "You answer questions based on the provided documents. "
        "If the answer is not found in the provided documents, say 'I don't know'. "
        "Always provide concise and accurate answers. Provide code snippets if necessary."
    )
)

HYDE_PROMPT = PromptTemplate.from_template(
    """You are a senior developer. Given the user's question about a codebase,
write a SHORT hypothetical code snippet that would answer it.
Only output the code, no explanation.

Question: {query}
Hypothetical code:"""
)

ANSWER_PROMPT = PromptTemplate.from_template(
    """Based on the following documents, answer this question: {query}

Documents:
{context}

Provide a concise and accurate answer only using the provided documents.
Include code snippets if necessary. If the answer is not found, say 'I don't know'."""
)

# ── Pipeline steps ─────────────────────────────────────────────────────────────

def _generate_hypothetical_doc(query: str) -> str:
    """HyDE step: generate a hypothetical code snippet to improve retrieval."""
    model = get_model()
    result = model.invoke(HYDE_PROMPT.format(query=query))
    return result.content


def _retrieve_documents(query: str, hypothetical_query: str, repo_name: str) -> list[Document]:
    """MMR retrieval using the combined real + hypothetical query."""
    db = get_vectorstore(repo_name)

    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 20,
            "lambda_mult": 0.6,
        },
    )

    # Combine real query + HyDE doc for richer embedding signal
    combined = f"{query}\n\n{hypothetical_query}"
    return retriever.invoke(combined)


def _format_context(docs: list[Document]) -> str:
    """
    Format retrieved docs into a compact context block.
    Including the source path helps the model attribute answers correctly
    and avoids hallucinating file names.
    """
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"# {source}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _generate_response(retrieved_docs: list[Document], query: str):
    """Final answer generation. Builds a fresh message list per call (thread-safe)."""
    model = get_model()
    context = _format_context(retrieved_docs)

    # Build messages fresh each call — the original mutated a module-level list,
    # which would bleed conversation history across unrelated user queries.
    messages = [
        SYSTEM_MESSAGE,
        HumanMessage(content=ANSWER_PROMPT.format(query=query, context=context)),
    ]

    return model.invoke(messages)


# ── Public entry point ─────────────────────────────────────────────────────────

def retrieval_pipeline(query: str, repo_name: str):
    """
    Run HyDE generation and document retrieval in parallel, then generate answer.

    HyDE generation and the initial retrieval setup are both I/O-bound (Ollama
    and Chroma calls). Running them concurrently cuts latency significantly —
    we don't need the hypothetical doc to start warming up the vectorstore.
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        hyde_future = executor.submit(_generate_hypothetical_doc, query)
        # Pre-warm the vectorstore connection while HyDE is generating
        store_future = executor.submit(get_vectorstore, repo_name)

        hypothetical_query = hyde_future.result()
        store_future.result()  # ensure connection is ready

    retrieved_docs = _retrieve_documents(query, hypothetical_query, repo_name)
    return _generate_response(retrieved_docs, query)


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else input("Repo (owner/repo): ")
    query = input("Enter your query: ")
    response = retrieval_pipeline(query, repo)
    print("\n" + "─" * 80)
    print(f"Query:    {query}")
    print("─" * 80)
    print(f"Response: {response.content}")
    print("─" * 80)