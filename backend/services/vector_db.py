import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# 👇 LIGHTWEIGHT GOOGLE EMBEDDINGS (No RAM usage on server)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def index_video_content(job_id: str, text: str):
    print(f"🔹 Indexing Start for Job: {job_id}")

    # 1. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)

    print(f"🔸 Split into {len(chunks)} chunks")

    # 2. Store in Pinecone (using Google Embeddings)
    try:
        PineconeVectorStore.from_texts(
            texts=chunks,
            embedding=embeddings,
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            namespace=job_id  # Using Job ID as namespace for isolation
        )
        print("✅ Indexing Success!")
        return True
    except Exception as e:
        print(f"❌ Indexing Failed: {e}")
        raise e
