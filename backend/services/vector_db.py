import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

os.environ['HF_HOME'] = r'D:\python_projects\veloce-ai\backend\model_cache'


def index_transcript(job_id: str, text: str, video_metadata: dict):
    """
    Ensures every single chunk has a string-based job_id for 100% retrieval accuracy.
    """
    print(f"🧠 Indexing for Job: {job_id}")

    # 1. Precise Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_text(text)

    # 👇 CRITICAL: Force job_id to string and replicate for ALL chunks
    job_id_str = str(job_id)
    metadatas = [{
        "job_id": job_id_str,
        "title": str(video_metadata.get('title', '')),
        "video_id": str(video_metadata.get('video_id', ''))
    } for _ in chunks]

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # 2. Upsert with explicit metadata mapping
    PineconeVectorStore.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        index_name=os.getenv("PINECONE_INDEX_NAME")
    )
    print(f"✅ Data indexed and searchable for Job: {job_id_str}")
