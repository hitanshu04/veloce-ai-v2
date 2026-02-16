#Import Statements
import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.audio_loader import download_audio, transcribe_audio
from services.vector_db import index_transcript
from services.chat_engine import get_chat_response, get_video_summary

app = FastAPI(title="Veloce-AI Backend")
app.add_middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_methods=["*"], allow_headers=["*"])

job_status_db = {}


class VideoRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    job_id: str
    question: str


@app.post("/process-video")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_status_db[job_id] = {"status": "queued", "step": "⏳ Starting..."}

    async def task():
        try:
            # 1. Download
            job_status_db[job_id]["step"] = "📥 Downloading..."
            file_path, title = await asyncio.to_thread(download_audio, request.url)

            # 2. Transcribe
            job_status_db[job_id]["step"] = "🎙️ Transcribing..."
            text = await asyncio.to_thread(transcribe_audio, file_path)

            # 🚨 CHECK: Stop if transcription failed
            if "TRANSCRIPTION_ERROR" in text:
                raise Exception(text.replace("TRANSCRIPTION_ERROR: ", ""))

            # 3. Index (Ab yahan tabhi pahuchega jab text VALID ho)
            job_status_db[job_id]["step"] = "🌲 Indexing to Vector DB..."
            await asyncio.to_thread(index_transcript, job_id, text)

            # 4. Summary
            job_status_db[job_id]["step"] = "📝 Generating 3-Point Summary..."
            summary = await asyncio.to_thread(get_video_summary, job_id)

            job_status_db[job_id] = {
                "status": "completed",
                "step": "✅ Ready",
                "summary": summary,
                "title": title
            }
        except Exception as e:
            # Clean up on failure
            print(f"❌ Task Error: {e}")
            job_status_db[job_id] = {
                "status": "failed", "step": f"Error: {str(e)}"}

    background_tasks.add_task(task)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return job_status_db.get(job_id, {"status": "not_found"})


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # ✅ Sequence sahi karo: Pehle QUESTION bhejona, fir JOB_ID
        answer = await asyncio.to_thread(
            get_chat_response,
            request.question,  # <--- Sawaal pehle
            request.job_id     # <--- ID baad mein
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
