from groq import Groq
import yt_dlp
from fastapi import FastAPI
import asyncio
import uuid
import os
from dotenv import load_dotenv
load_dotenv()  # 👈 Pehle load karo

# ... baaki imports iske baad ...

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def download_audio(url: str):
    # Ensure temp directory exists
    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '32',  # 🚀 EXTREME COMPRESSION: 32kbps keeps files tiny
        }],
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        # Force extension update to .m4a because of post-processor
        file_path = os.path.splitext(file_path)[0] + ".m4a"

        # Log size for debugging
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        print(f"📁 Downloaded file size: {file_size:.2f} MB")

        return file_path, info.get('title', 'Video')


def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as file:
            # Groq Whisper Call
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            return transcription
    except Exception as e:
        # 🚨 VERY IMPORTANT: Don't just return 'e', return a clear error flag
        print(f"❌ Transcription Failed: {str(e)}")
        return f"TRANSCRIPTION_ERROR: {str(e)}"
