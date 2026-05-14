from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

embeddings = OllamaEmbeddings(model="embeddinggemma")
persistent_directory = "db/chroma_db"

messages = [
        SystemMessage(content="You are a helpful assistant for software developers. You answer questions based on the provided documents. If the answer is not found in the provided documents, you say 'I don't know'. Always provide concise and accurate answers. Provide code snippets if necessary.")
    ]

db = Chroma(
        embedding_function=embeddings,
        persist_directory=persistent_directory,
        # collection_metadata={"hnsw:space": "cosine"},
    )

retriever = db.as_retriever(
        search_type="mmr", 
        search_kwargs={
            "k": 5,
            "fetch_k": 20,
            "lambda_mult":0.6 
            }
        )


def generate_pipeline(query):
    """This is a function to create a sample code for retrieval."""

    model = ChatOllama(model="minimax-m2.5:cloud")

    hyde_prompt = PromptTemplate.from_template("""
                    You are a senior developer. Given the user's question about a codebase, 
                    write a SHORT hypothetical code snippet that would answer it.
                    Only output the code, no explanation.

                    Question: {query}
                    Hypothetical code:
                    """)
    
    hypothetical_doc = model.invoke(hyde_prompt.format(query=query))
    # Embed that instead of the raw question
    return hypothetical_doc.content


def retrieve_documents(query):
    """This function retrieves relevant documents based on the query"""

    relevant_chunks = retriever.invoke(query)

    # for i, chunk in enumerate(relevant_chunks):
    #     print(f"Chunk {i+1}:")
    #     print(f"Source: {chunk.metadata['source']}")
    #     print(f"content: {chunk.page_content}")
    #     print("-------------------------------------------------------")

    return relevant_chunks, retriever


def generate_response(retrieved_docs, query):
    """This function generates a response based on the retrieved documents and the query"""

    final_query = f"Based on the following documents, answer this question: {query}\n\n \
        Documents:{retrieved_docs}\n \
        Please provide a concise and accurate answer only using the provided documents. Provide code snippets if necessary. If the answer is not found in the retrieved documents, just say 'I don't know'."

    model = ChatOllama(model="minimax-m2.5:cloud")

    messages.append(HumanMessage(content=final_query))

    result = model.invoke(messages)

    return result


def retrieval_pipeline(query):
    hypothetical_query = generate_pipeline(query)
    retrieved_docs = retrieve_documents(hypothetical_query)
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