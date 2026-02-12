import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.audio_loader import download_audio, transcribe_audio
from services.vector_db import index_transcript
from services.chat_engine import get_chat_response

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
            video_data = await asyncio.to_thread(download_audio, request.url)
            text = await asyncio.to_thread(transcribe_audio, video_data['audio_path'])
            await asyncio.to_thread(index_transcript, job_id, text, video_data)
            job_status_db[job_id] = {"status": "completed", "step": "✅ Ready"}
        except Exception as e:
            job_status_db[job_id] = {"status": "failed", "step": str(e)}

    background_tasks.add_task(task)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str): return job_status_db.get(
    job_id, {"status": "not_found"})


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer = await asyncio.to_thread(get_chat_response, request.job_id, request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
