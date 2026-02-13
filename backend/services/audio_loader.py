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

    # --- PLAN A: Try Fetching Direct Transcript (Fastest) ---
    try:
        print("⚡ Attempting Plan A: Direct Transcript Fetch...")
        # Hindi, English (US/UK), aur Auto-generated sab try karega
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
        print(f"⚠️ Plan A Failed ({e}). Switching to Plan B...")

    # --- PLAN B: Download Audio & Use AI (Fallback) ---
    print("🐢 Attempting Plan B: Audio Download + Whisper AI...")

    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best',  # M4A is fastest for Whisper
            'outtmpl': 'temp_audio/%(id)s.%(ext)s',
            'cookiefile': 'cookies.txt',  # Blocking bachane ke liye
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'Video')

    except Exception as e:
        print(f"❌ Plan B also Failed: {e}")
        raise Exception(
            "Failed to process video via both Transcript and Audio methods.")


def transcribe_audio(file_path: str):
    print(f"🚀 Processing Content: {file_path}")

    try:
        # Check 1: Agar file .txt hai (Plan A se aayi hai)
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        # Check 2: Agar file Audio hai (Plan B se aayi hai)
        # Tab hum Groq Whisper use karenge
        with open(file_path, "rb") as file:
            print("🎙️ Sending Audio to Groq Whisper...")
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
            return transcription.text

    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🗑️ Cleanup Done")
