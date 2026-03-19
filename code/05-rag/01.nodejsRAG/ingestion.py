from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os


load_dotenv()

# Loading
loader = PyPDFLoader(file_path=".//nodejs.pdf")
docs = loader.load()  # Read PDF File

# Chunking
'''
    Here, we are taking the chunk size as 1000 words, and 400 word overlap. This overlap is just for context from the previous chunk's data. 400 words from previous chunk and 600 from new chunk.
'''
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

split_docs = text_splitter.split_documents(documents=docs)


# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    api_key=os.getenv("OPEN_AI_API_KEY"),
    model="text-embedding-3-large"
)

# Using [embedding_model] create embeddings of [split_docs] and store in DB
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Indexing of Documents Done...")