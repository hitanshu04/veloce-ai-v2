import os
import httpx  # 👈 Zaroori hai Compatibility ke liye
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# 👇 Consistent Embeddings (Must match vector_db.py)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 👇 PROXY FIX: Manual client define kar rahe hain taaki 'proxies' error na aaye
custom_client = httpx.Client()

# LLM (Brain)
llm = ChatGroq(
    temperature=0.3,
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    http_client=httpx.Client()  # 👈 Explicitly pass a clean client
)

vectorstore = PineconeVectorStore(
    index_name=os.getenv("PINECONE_INDEX_NAME"),
    embedding=embeddings
)


def get_chat_response(job_id: str, question: str):
    print(f"🔍 Searching for Job ID: {job_id}")

    # Namespace zaroori hai taaki sirf usi video se answer mile
    retriever = vectorstore.as_retriever(
        search_kwargs={'k': 5, 'namespace': job_id}
    )

    template = """SYSTEM: You are Veloce-AI. Answer based ONLY on the context below.
    If context is empty, say "I don't have info on this part of the video."
    
    CONTEXT:
    {context}

    USER QUESTION: {question}
    
    ANSWER:"""

    prompt = ChatPromptTemplate.from_template(template)

    # Chain setup
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke(question).strip()
