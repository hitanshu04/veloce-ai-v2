import os
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient  # <--- Official SDK
from pinecone import Pinecone

load_dotenv()
client = InferenceClient(token=os.getenv("HF_TOKEN"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))


def get_hf_embeddings(texts):
    """SDK based embeddings: 404/410 proof"""
    model_id = "sentence-transformers/all-MiniLM-L6-v2"

    while True:
        try:
            # SDK handles the endpoint URL automatically
            embeddings = client.feature_extraction(texts, model=model_id)

            # Python 3.14 check: sometimes returns as nested lists
            if isinstance(embeddings, list):
                return embeddings
            return embeddings.tolist()  # If it's a numpy-like array

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "loading" in error_msg.lower():
                print("⏳ Model is loading on Hugging Face... waiting 15s")
                time.sleep(15)
                continue
            else:
                print(f"❌ SDK Error: {e}")
                time.sleep(5)
                continue


def index_transcript(video_id, transcript_text):
    try:
        # 1. Text Splitter
        chunks = [transcript_text[i:i+1000]
                  for i in range(0, len(transcript_text), 1000)]
        print(f"🌲 Indexing {len(chunks)} chunks...")

        # 2. Get Embeddings via SDK
        embeddings = get_hf_embeddings(chunks)

        # 3. Upsert to Pinecone
        vectors = []
        for i, emb in enumerate(embeddings):
            vectors.append({
                "id": f"{video_id}_{i}",
                "values": emb,
                "metadata": {"text": chunks[i], "source": video_id}
            })

        index.upsert(vectors=vectors)
        print("✅ Indexing Complete!")
    except Exception as e:
        print(f"❌ Indexing Error: {e}")
        raise e
