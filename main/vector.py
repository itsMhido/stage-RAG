from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os

# --- Load text files ---
base_dir = os.path.dirname(os.path.abspath(__file__))
text_folder = os.path.join(base_dir, "..", "ocr_results")

docs = []
ids = []

# Read all .txt files in the folder
for idx, filename in enumerate(os.listdir(text_folder)):
    if filename.lower().endswith(".txt"):
        file_path = os.path.join(text_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                continue  # skip empty files
            docs.append(Document(
                page_content=content,
                metadata={"source": filename},
                id=str(idx)
            ))
            ids.append(str(idx))

# --- Embeddings & Vector Store ---
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chroma_db"
add_docs = not os.path.exists(db_location)

vector_store = Chroma(
    collection_name="my_collection",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_docs:
    vector_store.add_documents(documents=docs, ids=ids)

# --- Retriever ---
retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)
