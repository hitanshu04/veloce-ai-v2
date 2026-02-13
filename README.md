# ⚡ Veloce-AI: Intelligent Video RAG Engine

**Veloce-AI** is a high-performance Video Intelligence platform that allows users to chat with YouTube videos in real-time. By leveraging a state-of-the-art RAG (Retrieval-Augmented Generation) pipeline, it delivers automated summaries and precise context-aware answers.

---

## 🚀 Key Features

- **Automated Takeaways:** Generates a 3-point executive summary as soon as video indexing completes.
- **Real-time Video Chat:** Query any part of the video using Llama 3.3.
- **Extreme Audio Compression:** Optimized ingestion for long-form content.

---

## 🛠️ Technical Architecture & Challenges

### **The "Payload Constraint" Solution**

One major challenge was the **413 Request Entity Too Large** error from the Groq Whisper API (25MB limit).

- **Solution:** I implemented a custom audio processing pipeline using `yt-dlp` and `ffmpeg` to extract **32kbps M4A audio-only streams**.
- **Impact:** Reduced file sizes by ~60%, enabling the processing of 1-hour+ videos within API constraints without losing transcription quality.

### **High-Speed RAG Pipeline**

- **Vector Database:** Utilizes **Pinecone** for low-latency similarity searches.
- **LLM Reasoning:** Powered by **Groq's Llama-3.3-70b-versatile** for sub-second responses.
- **Filtering:** Implemented strict metadata filtering to ensure zero cross-talk between different video sessions.

---

## 💻 Tech Stack

- **Frontend:** Next.js (App Router), Tailwind CSS
- **Backend:** FastAPI, Python 3.14 (Bleeding Edge)
- **AI/ML:** HuggingFace Hub SDK, Groq Whisper-v3, Llama 3.3
- **Database:** Pinecone Vector DB

---

## 🔧 Installation & Setup

1. Clone the repo: `git clone https://github.com/hitanshu04/veloce-ai.git`
2. Set up environment variables in a `.env` file (refer to `.env.example`).
3. Run Backend: `uvicorn main:app --reload`
4. Run Frontend: `npm run dev`

Created by [Hitanshu Kumar Singh](https://www.linkedin.com/in/hitanshu-kumar-singh-7a98041b0/)
