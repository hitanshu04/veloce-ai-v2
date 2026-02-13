import os
from huggingface_hub import InferenceClient
from langchain_groq import ChatGroq
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
client = InferenceClient(token=os.getenv("HF_TOKEN"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
llm = ChatGroq(groq_api_key=os.getenv(
    "GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")


def get_chat_response(query, video_id):
    try:
        # 1. Embed Query via SDK
        query_emb = client.feature_extraction(
            query, model="sentence-transformers/all-MiniLM-L6-v2")

        # 2. Search Pinecone
        search_res = index.query(vector=query_emb.tolist() if hasattr(query_emb, 'tolist') else query_emb,
                                 top_k=3, include_metadata=True, filter={"source": video_id})

        matches = search_res.get('matches', [])
        context = " ".join([m.get('metadata', {}).get('text', '')
                           for m in matches])

        # 3. LLM Response
        prompt = f"Using this context: {context}\n\nQuestion: {query}"
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Chat Error: {str(e)}"

# Isse chat_engine.py ke end mein add kar de


def get_video_summary(video_id):
    """Generates a 3-point summary automatically after indexing"""
    try:
        # 1. Broad context ke liye hum khali query bhejte hain (Top 5 chunks)
        # Summary ke liye humein query ki zarurat nahi, bas video_id ka context chahiye
        search_res = index.query(
            vector=[0] * 384,  # Dummy vector for broad search
            top_k=5,
            include_metadata=True,
            filter={"source": video_id}
        )

        matches = search_res.get('matches', [])
        context = " ".join([m.get('metadata', {}).get('text', '')
                           for m in matches])

        # 2. Specialized Summary Prompt
        summary_prompt = (
            f"Analyze the following video transcript context and provide exactly 3 concise, "
            f"high-impact takeaways or a summary. Use bullet points.\n\nContext: {context}"
        )

        # 3. Use Llama 3.3 for the summary
        response = llm.invoke(summary_prompt)
        return response.content
    except Exception as e:
        print(f"⚠️ Summary Generation Failed: {e}")
        return "Summary generation failed, but you can still chat with the video!"
