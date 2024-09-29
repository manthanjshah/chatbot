import argparse
import os
import shutil
import faiss
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain.vectorstores import FAISS
from get_embeddings_function import get_embedding_function
import time

# Updated FAISS_PATH to be a directory, not a file.
FAISS_PATH = r"C:\Users\Manthan Jigar shah\ml learning\chatbot\data\faiss_index"
DATA_PATH = r"C:\Users\Manthan Jigar shah\ml learning\chatbot\data"

# Global chat context
CHAT_HISTORY = ""


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_faiss(chunks: list[Document]):
    # Load the FAISS database or create a new one.
    embedding_function = get_embedding_function()
    db = FAISS.from_documents(chunks, embedding_function)

    # Persist the FAISS index.
    db.save_local(FAISS_PATH)
    print(f"FAISS index saved at {FAISS_PATH}")


def clear_database():
    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def query_rag(query_text: str, chat_history: str):
    # Start total timer
    total_start_time = time.time()

    # Prepare the DB (time FAISS loading)
    embedding_function = get_embedding_function()

    faiss_load_start = time.time()
    db = FAISS.load_local(FAISS_PATH, embedding_function, allow_dangerous_deserialization=True)
    faiss_load_end = time.time()
    faiss_load_time = faiss_load_end - faiss_load_start

    # Search the DB (time FAISS search)
    faiss_search_start = time.time()
    results = db.similarity_search_with_score(query_text, k=2)
    print(results)
    faiss_search_end = time.time()
    faiss_search_time = faiss_search_end - faiss_search_start

    # Combine the previous chat history with the current context
    context_text = chat_history + "\n\n---\n\n" + "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Prepare the prompt (template formatting)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Model inference (time model response)
    model = Ollama(model="phi3")
    model_inference_start = time.time()
    response_text = model.invoke(prompt)
    model_inference_end = time.time()
    model_inference_time = model_inference_end - model_inference_start

    # Limit the response to 5 lines
    response_lines = response_text.split('\n')
    response_text_limited = '\n'.join(response_lines[:5])

    # Collect sources
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text_limited}\nSources: {sources}"

    # End total timer
    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    # Print the time taken for each step
    print(f"FAISS Load Time: {faiss_load_time:.4f} seconds")
    print(f"FAISS Search Time: {faiss_search_time:.4f} seconds")
    print(f"Model Inference Time: {model_inference_time:.4f} seconds")
    print(f"Total Time: {total_time:.4f} seconds")

    # Return the response text and updated chat history
    chat_history += f"\n\n---\n\nUser: {query_text}\n\n---\n\nBot: {response_text_limited}"
    return response_text_limited, chat_history



def main():
    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()


    # Keep a global chat history
    global CHAT_HISTORY
    while True:
        query_text = input("Please enter your query (or type 'exit' to quit): ")
        if query_text.lower() == 'exit':
            print("Ending the session. Goodbye!")
            break

        # Query the model and update chat history
        response_text, updated_context = query_rag(query_text, CHAT_HISTORY)
        CHAT_HISTORY = updated_context
        print(response_text)


if __name__ == "__main__":
    main()
