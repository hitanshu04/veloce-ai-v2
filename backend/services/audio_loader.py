import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def download_audio(url: str):
    print(f"⬇️ Downloading: {url}")
    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")

    ydl_opts = {
        # 'best' maang rahe hain taaki 'format not available' error na aaye
        'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # 👈 Ye GitHub par honi zaroori hai!
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Video')
    except Exception as e:
        print(f"❌ YouTube Error: {e}")
        raise Exception(f"YouTube Blocked: {str(e)}")


def transcribe_audio(file_path: str):
    print(f"🚀 Transcribing: {file_path}")
    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
        return transcription.text
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
