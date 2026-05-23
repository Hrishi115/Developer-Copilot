from ingestion_pipeline import load_documents, chunking_documents, create_vector_collection
from retrieval_pipeline import retrieval_pipeline, messages
from langchain_core.messages import AIMessage, HumanMessage 
from langchain_ollama import ChatOllama
import os

def orchestrator():
    """This function orchestrates the entire process of ingestion and retrieval."""
    print("Welcome to the Developer Copilot!")
    print("To begin enter your github repository ([owner/repo] for example: langchain-ai/langchain)")
    repository = str(input("Repository: "))
    print("----------------------------------------")
    print("Loading documents from the repository...")
    print("----------------------------------------")

    documents = load_documents(repository)
    print("----------------------------------------")
    print("Documents Loaded Successfully!")
    print("----------------------------------------")

    print("Chunking the documents...")
    chunks = chunking_documents(documents)
    print("----------------------------------------")

    print("Creating vector store...")
    vector_store = create_vector_collection(repository, chunks)
    print("----------------------------------------")

    print("Now you can ask questions about the codebase!")
    print("To exit, type 'exit()'\n\n")

    query = input("Enter your query: ")
    response = retrieval_pipeline(query, repository)
    print("----------------------------------------")
    print("Response:", response.content)

    messages.append(AIMessage(content=response.content))
    while True:
        if query.lower().strip() == "exit":
            print("Exiting the Developer Copilot. Goodbye!")
            break
        query = input("\n\nEnter follow-up question: ")
        messages.append(HumanMessage(content=query))
        response = ChatOllama(model="minimax-m2.5:cloud").invoke(messages)
        print("-"*40)
        print("\nResponse:", response.content)
        messages.append(AIMessage(content=response.content))

if __name__ == "__main__":
    orchestrator()
