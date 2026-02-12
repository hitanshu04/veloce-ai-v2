import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ensure directory exists
if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def download_audio(url: str):
    print(f"⬇️ 2026 Browser-Impersonation Mode: {url}")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/best',
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # 👇 BYPASS LOGIC
        'impersonate_base_headers': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Video')
    except Exception as e:
        print(f"❌ Blocked: {e}")
        raise Exception(f"YouTube Blocked the Bot: {str(e)}")

# 👇 YE FUNCTION MISSING THA (IMPORT ERROR FIX)


def transcribe_audio(file_path: str):
    print(f"🚀 Transcribing: {file_path}")
    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
        print("✅ Transcription Complete!")
        return transcription.text
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        raise Exception("Transcription failed via Groq.")
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
