from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

embeddings = OllamaEmbeddings(model="nomic-embed-text")
persistent_directory = "db/chroma_db"

def retrieve_documents(query):
    """This function retrieves relevant documents based on the query"""
    db = Chroma(
        embedding_function=embeddings,
        persist_directory=persistent_directory,
        # collection_metadata={"hnsw:space": "cosine"},
    )

    retriever = db.as_retriever(search_kwargs={"k": 5})

    relevant_chunks = retriever.invoke(query)

    for i, chunk in enumerate(relevant_chunks):
        print(f"Chunk {i+1}:")
        print(f"Source: {chunk.metadata['source']}")
        print(f"content: {chunk.page_content}")
        print("-------------------------------------------------------")

    return relevant_chunks

def generate_response(retrieved_docs, query):
    """This function generates a response based on the retrieved documents and the query"""

    final_query = f"Based on the following documents, answer this question: {query}\n\n \
        Documents:{retrieved_docs}\n \
        Please provide a concise and accurate answer only using the provided documents. Provide code snippets if necessary. If the answer is not found in the retrieved documents, just say 'I don't know'."

    model = ChatOllama(model="minimax-m2.5:cloud")

    messages = [
        SystemMessage(content="You are a helpful assistant for software developers. You answer questions based on the provided documents. If the answer is not found in the provided documents, you say 'I don't know'. Always provide concise and accurate answers. Provide code snippets if necessary."),
        HumanMessage(content=final_query)
    ]

    result = model.invoke(messages)

    return result

def retrieval_pipeline(query):
    retrieved_docs = retrieve_documents(query)
    
    response = generate_response(retrieved_docs, query)
    
    return response

if __name__ == "__main__":
    query = str(input("Enter your query: "))
    response = retrieval_pipeline(query)
    print("--------------------------------------------------------------------------------------")
    print("Query: ", query)
    print("------------------")
    print("Response: ", response.content)
    print("--------------------------------------------------------------------------------------")