from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader,PyPDFLoader,BSHTMLLoader,JSONLoader,CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import os
from langchain_chroma import Chroma
from state import AgentState

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

api = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIRECTORY")
CHROMA_COLLECTON_NAME = os.getenv("CHROMA_COLLECTION_NAME")



def load_text_file(text_files : list[Path]) -> list[Document]:
    
    documents = []
    for file_path in text_files:
        loader = TextLoader(str(file_path),encoding="utf-8")
        docs = loader.load()

        # adding metadata
        for doc in docs:
            doc.metadata.update({
                "source":file_path.name,
                "file_path":str(file_path),
                "file_type":"txt"
            })
        documents.extend(docs)
    print(f"loaded {len(documents)} text documents.")

    return documents

def load_pdf_file(pdf_files : list[Path]) -> list[Document]:

    documents = []
    for file_path in pdf_files:
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()

        for doc in docs:
            doc.metadata.update({
                "source":file_path.name,
                "file_path":str(file_path),
                "file_type":"pdf"
            })
        documents.extend(docs)
    print(f"Loaded {len(documents)} PDF Documents.")

    return documents
    
def load_html_file(html_files : list[Path]) -> list[Document]:

    documents = []
    for file_path in html_files:
        loader = BSHTMLLoader(str(file_path))
        docs = loader.load()

        for doc in docs:
            doc.metadata.update({
                "source":file_path.name,
                "file_path":str(file_path),
                "file_type":"html"
            })
        documents.extend(docs)
    print(f"Loaded {len(documents)} HTML documents")

    return documents

def load_csv_file(csv_files : list[Path]) -> list[Document]:

    documents = []
    for file_path in csv_files:
        loader = CSVLoader(str(file_path), encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata.update({
                "source":file_path.name,
                "file_path":str(file_path),
                "file_type":"csv"
            })      
        documents.extend(docs)
    print(f"Loaded {len(documents)} CSV documents.")
    return documents


def load_json_file(json_files : list[Path]) -> list[Document]:

    documents = []

    for file_path in json_files:
        loader = JSONLoader(str(file_path),
                             jq_schema=".[]",
                             text_content=False
                             )
        docs = loader.load()

        for doc in docs:
            doc.metadata.update({
                "source":file_path.name,
                "file_path":str(file_path),
                "file_type":"json"
            })
        documents.extend(docs)
    print(f"Loaded {len(documents)} JSON documents")
    return documents


def chunk_all_documents(documents : list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
            chunk_size= 500,
            chunk_overlap=50,
            length_function=len,
            add_start_index=True
        )
    chunked_documents = splitter.split_documents(documents)
    return chunked_documents


# Helper method to call all loaders in ingestion pipeline
def load_all_documents(data_dir : list[Path]) -> list[Document]:

    documents = []
    txt_files = list(data_dir.rglob("*.txt"))
    pdf_files = list(data_dir.rglob("*.pdf"))
    html_files = list(data_dir.rglob("*.html"))
    csv_files = list(data_dir.rglob("*.csv"))
    json_files = list(data_dir.rglob("*.json"))

    documents.extend(load_html_file(html_files))
    documents.extend(load_text_file(txt_files))
    documents.extend(load_pdf_file(pdf_files))
    documents.extend(load_csv_file(csv_files))
    documents.extend(load_json_file(json_files))


    return documents

# embeddings
# ---------------------------------------------------------------------------

def create_embeddings():

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=api
    )

    return embeddings
# ---------------------------------------------------------------------------

# vectorestore
def create_vector_store(chunks : list[Document],embeddings):

    vectorestore = Chroma(
        collection_name=CHROMA_COLLECTON_NAME,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )
    vectorestore.add_documents(chunks)

    return vectorestore


def retrive_chunks(state : AgentState):

    query = state['question']

    embeddings = create_embeddings()

    vector_store = Chroma(
        collection_name=CHROMA_COLLECTON_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    retriver = vector_store.as_retriever(
        search_kwargs = {
            "k":4
        }
    )
    documents = retriver.invoke(query)
    return {
        "documents":documents
    }




# if __name__ == "__main__":

#     documents = load_all_documents(DATA_DIR)

#     chunks = chunk_all_documents(documents)

#     print(f"Total documents: {len(documents)}")
#     print(f"Total chunks: {len(chunks)}")

#     for i, chunk in enumerate(chunks[:3]):
#         print("=" * 60)
#         print(f"Chunk {i + 1}")
#         print("-" * 60)
#         print(chunk.page_content)
#         print("-" * 60)
#         print("Metadata:")
#         print(chunk.metadata)

#     embeddings = create_embeddings()

#     create_vector_store(chunks, embeddings)

#     print("Vector store created successfully.")

#     # Test code snippet
#     # ----------------------------------------
#     # state = {
#     #     "question": "What is the return policy?",
#     #     "answer": "",
#     #     "use_rag": True,
#     #     "documents": []
#     # }

#     # result = retrive_chunks(state)

#     # documents = result["documents"]

#     # print(f"\nRetrieved documents: {len(documents)}")

#     # for doc in documents:
#     #     print(f"Content: {doc.page_content}")
#     #     print(f"Metadata: {doc.metadata}")
#     #     print("-" * 50)