from langchain_community.document_loaders import GithubFileLoader
from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
import os
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
    ".html", ".css", ".json", ".yaml", ".yml", ".md", ".txt"
}
IGNORED_DIRS = {"migrations", "alembic", "node_modules", "dist", "build", ".vite"}
IGNORED_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "vite.config.js", 
                "vite.config.ts", "eslint.config.js", "package.json", "tsconfig.json", 
                "webpack.config.js", "babel.config.js"}

def should_load(path: str) -> bool:
    parts = path.split("/")
    if set(parts) & IGNORED_DIRS:   
        return False
    if path.split("/")[-1] in IGNORED_FILES: 
        return False
    return any(path.endswith(ext) for ext in ALLOWED_EXTENSIONS)


def load_documents(repo_name: str) -> list:
    """This function loads documents from the specified path."""
    loader = GithubFileLoader(
    repo=repo_name,  # the repo name
    branch="main",  # the branch name
    access_token=os.getenv("ACCESS_TOKEN"),
    github_api_url="https://api.github.com",
    file_filter=should_load,  # load all allowed files.
    )

    paths = loader.get_file_paths()
    
    documents = []

    for file  in paths:
        path = file["path"]
        
        try:
            content = loader.get_file_content_by_path(path)
        except Exception as e:
            print(f"[Warning]: skipping {path} : {e}")
            continue
        
        if content:
            ext = os.path.splitext(path)[1]
            documents.append(
                Document(page_content=content, metadata={"source": path, "repo": repo_name, "Language": ext.lstrip(".")})
            )
        
    with open("documents.txt", "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(f"Source: {doc.metadata['source']}\n")
            f.write(f"Repo: {doc.metadata['repo']}\n")
            f.write(f"Content:\n{doc.page_content}\n")
            f.write("-" * 80 + "\n")

    return documents


def chunking_documents(documents: list, chunk_size=800, chunk_overlap=100) -> list:
    """This function chunks the documents into smaller pieces."""
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\nclass ", "\ndef ","\nasync def ","\n@","\n\n"],
        chunk_size=800,
        chunk_overlap=100
    )
    for doc in documents:
        # ext = "." + doc.metadata.get("Language", "text").lower()
        # lang = EXT_TO_LANGUAGE.get(ext)
        chunks.extend(text_splitter.split_documents([doc]))

    return chunks

def create_vector_store(chunks: list, persistent_directory: str = "db/chroma_db") -> None:
    """This function creates a vector store from the chunks."""
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vector_store = Chroma.from_documents(
        embedding=embeddings,
        documents=chunks,
        persist_directory=persistent_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print("Created Vector Store")

    return vector_store

if __name__ == "__main__":

    repo_name = input("Enter the GitHub repository name (e.g., owner/repo): ")
    docs = load_documents(repo_name)

    chunks = chunking_documents(docs)
    
    # for i, chunk in enumerate(chunks[:5]):
    #     print(f"Chunk {i+1}:")
    #     print(f"Source: {chunk.metadata['source']}")
    #     print(f"content: {chunk.page_content}")
    #     print("-------------------------------------------------------")
    
    # print(docs)

    vector_store = create_vector_store(chunks)