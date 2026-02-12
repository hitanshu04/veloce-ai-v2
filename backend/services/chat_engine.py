import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

os.environ['HF_HOME'] = r'D:\python_projects\veloce-ai\backend\model_cache'

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

llm = ChatGroq(
    temperature=0.1,  # Thoda sa creativity badhaya taaki wo connect kar sake
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

vectorstore = PineconeVectorStore(
    index_name=os.getenv("PINECONE_INDEX_NAME"),
    embedding=embeddings
)


def get_chat_response(job_id: str, question: str):
    job_id_str = str(job_id)
    print(f"🔍 RAG: Searching Pinecone for Job ID: {job_id_str}")

    retriever = vectorstore.as_retriever(
        search_kwargs={'filter': {'job_id': job_id_str}, 'k': 5}
    )

    # 👇 THE SMART ANALYST PROMPT (Ad-Filter Added)
    template = """SYSTEM: You are Veloce-AI, an expert video analyst. 
    
    CORE INSTRUCTIONS:
    1. **Identify the Main Topic:** Look at the 'VIDEO CONTEXT' broadly. Distinguish between the **Main Story/Content** and **Sponsorship Segments**.
    2. **Handle Sponsorships:** If the transcript talks about a product (e.g., Samsung, Dream11, Mamaearth) in a promotional tone, REALIZE that this is just an ad, NOT the main topic.
    3. **Prioritize the Story:** Your answer must focus 90% on the main sketch, tutorial, or story, and only mention the sponsorship if explicitly asked or as a side note.
    4. **Language Rule:** Answer STRICTLY in the language of the 'USER QUESTION'.

    Example Logic:
    - If video is a comedy sketch but has a 2-minute phone ad:
    - BAD Answer: "The video is about a phone launch."
    - GOOD Answer: "The video is a comedy sketch about [Topic]. It also features a promotional segment for a phone."

    VIDEO CONTEXT:
    {context}

    USER QUESTION: {question}
    
    FINAL ANSWER:"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = ({"context": retriever, "question": RunnablePassthrough()}
             | prompt | llm | StrOutputParser())

    try:
        return chain.invoke(question).strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't analyze the video content properly."
