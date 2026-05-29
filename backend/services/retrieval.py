# from langchain_chroma import Chroma
# from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
# from functools import lru_cache
# from concurrent.futures import ThreadPoolExecutor, as_completed
from services.models import Models
from database.vectorstore import supabase
import asyncio



# ── Shared instances (created once per process, not per call) ─────────────────

# @lru_cache(maxsize=1)
# def get_embeddings() -> OllamaEmbeddings:
#     return OllamaEmbeddings(model="embeddinggemma")

# @lru_cache(maxsize=1)
# def get_model() -> ChatOllama:
#     return ChatOllama(model="minimax-m2.5:cloud")

# @lru_cache(maxsize=16)
# def get_vectorstore(repo_name: str, persistent_directory: str = "db/chroma_db") -> Chroma:
#     """
#     Cache open Chroma collections by repo name.
#     maxsize=16 covers 16 different repos before evicting the oldest —
#     fine for MVP with 20-30 devs testing a handful of repos.
#     """
#     return Chroma(
#         embedding_function=get_embeddings(),
#         persist_directory=persistent_directory,
#         collection_name=repo_name.replace("/", "_"),
#     )

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
    model = Models.get_llm()
    result = model.generate_content(HYDE_PROMPT.format(query=query))
    return result.text


def _retrieve_documents(query: str, hypothetical_query: str, repo_name: str) -> list[Document]:
    """MMR retrieval using the combined real + hypothetical query."""
    # db = get_vectorstore(repo_name)
    # Combine real query + HyDE doc for richer embedding signal
    combined = f"{query}\n\n{hypothetical_query}"
    
    # query_embedding = Models.embedding_model(combined)
    filter_source = repo_name.replace("/", "_")
    print(f"[DEBUG] Querying with filter_source: {filter_source}")
    query_embedding = Models.embedding_model(combined)

    print(f"[DEBUG] Embedding type: {type(query_embedding)}")
    print(f"[DEBUG] Embedding length: {len(query_embedding)}")
    print(f"[DEBUG] First element type: {type(query_embedding[0])}")
    print(f"[DEBUG] First 3 values: {query_embedding[:3]}")

    query_embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    try:
        result = supabase.rpc("match_documents", {
            "query_embedding":query_embedding_str,
            "match_count": 20,
            "filter_source": repo_name.replace("/", "_"), 
        }).execute()

        print(f"[DEBUG] Result: {result}")
        print(f"[DEBUG] Data: {result.data}")
        print(f"[DEBUG] Count: {len(result.data)}")

    except Exception as e:
        print(f"[Error] Supabase RPC failed: {e}")
        return []
    # retriever = db.as_retriever(
    #     search_type="mmr",
    #     search_kwargs={
    #         "k": 5,
    #         "fetch_k": 20,
    #         "lambda_mult": 0.6,
    #     },
    # )

    if not result.data:
        return []

    docs = []
    for row in result.data:
        print(f"[DEBUG] similarity={row.get('similarity'):.3f} | file={row.get('file_path')}")
        if not row.get("content"):  # ensure we don't include empty docs
            continue
        docs.append(
            Document(
                page_content=row.get("content"),
                metadata={
                    "source": row.get("file_path"),
                    "repo_name": row.get("source"),
                },
            )
        )

    return docs


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
    model = Models.get_llm()
    context = _format_context(retrieved_docs)

    # Build messages fresh each call — the original mutated a module-level list,
    # which would bleed conversation history across unrelated user queries.
    full_prompt = f"""
        "You are a helpful assistant for software developers. "
        "You answer questions based on the provided documents. "
        "If the answer is not found in the provided documents, say 'I don't know'. "
        "Always provide concise and accurate answers. Provide code snippets if necessary."
    
    {ANSWER_PROMPT.format(query=query, context=context)}
    """

    output = model.generate_content(full_prompt)
    return output.text

# ── Public entry point ─────────────────────────────────────────────────────────

def retrieval_pipeline(query: str, repo_name: str) -> str:
    """
    Run HyDE generation and document retrieval in parallel, then generate answer.

    HyDE generation and the initial retrieval setup are both I/O-bound (Ollama
    and Chroma calls). Running them concurrently cuts latency significantly —
    we don't need the hypothetical doc to start warming up the vectorstore.
    """
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     hyde_future = executor.submit(_generate_hypothetical_doc, query)

    #     hypothetical_query = hyde_future.result()

    hypothetical_query = _generate_hypothetical_doc(query)
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