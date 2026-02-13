import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def get_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None


def download_audio(url: str):
    print(f"🔄 Processing Video: {url}")
    video_id = get_video_id(url)

    # --- PLAN A: Transcript (Fastest) ---
    try:
        print("⚡ Attempting Plan A: Direct Transcript Fetch...")
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['hi', 'en', 'en-US', 'en-GB'])

        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript)

        filename = f"temp_audio/{video_id}_transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text_formatted)

        print("✅ Plan A Successful! (Direct Text)")
        return filename, "YouTube Video (Transcript)"

    except Exception as e:
        print(f"⚠️ Plan A Failed (No Captions). Switching to Plan B...")

    # --- PLAN B: Format 18 Download (Robust Fallback) ---
    print("🐢 Attempting Plan B: Downloading Format 18 (No FFmpeg needed)...")

    try:
        ydl_opts = {
            # 👇 MAGIC FIX: Format 18 = Pre-merged Audio/Video.
            # FFmpeg ke bina yahi chalta hai Render par.
            'format': '18',
            'outtmpl': 'temp_audio/%(id)s.%(ext)s',
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"✅ Plan B Successful! File: {filename}")
            return filename, info.get('title', 'Video')

    except Exception as e:
        print(f"❌ Plan B also Failed: {e}")
        # Agar ye bhi fail hua matlab YouTube ne IP block kar diya hai
        raise Exception(f"Video process nahi ho paayi. Reason: {str(e)}")


def transcribe_audio(file_path: str):
    print(f"🚀 Processing Content: {file_path}")

    try:
        # Case 1: Text File (Plan A)
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        # Case 2: Video/Audio File (Plan B)
        with open(file_path, "rb") as file:
            print("🎙️ Sending to Whisper...")
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
            return transcription.text

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🗑️ Cleanup Done")
