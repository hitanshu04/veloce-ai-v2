import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Setup Groq Client (Ye hai Speed ka Raaz 🚀)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ensure temp directory exists
if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def download_audio(url: str):
    """
    Downloads audio from YouTube URL using yt-dlp (Fastest format).
    """
    print(f"⬇️ Downloading Audio: {url}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"temp_audio/{info['id']}.mp3"
            return filename, info.get('title', 'Unknown Video')
    except Exception as e:
        print(f"❌ Download Error: {e}")
        raise Exception("Failed to download video audio.")


def transcribe_audio(file_path: str):
    """
    Uses Groq API (Whisper-Large-V3) for Ultra-Low Latency Transcription.
    Converts Audio -> Text in seconds.
    """
    print(f"🚀 Transcribing with Groq API: {file_path}")

    try:
        with open(file_path, "rb") as file:
            # Groq ka magic call - Super Fast ⚡
            transcription = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",  # World's fastest model currently
                response_format="json",
                temperature=0.0
            )

        print("✅ Transcription Complete!")
        return transcription.text

    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        raise Exception("Transcription failed via Groq API.")
    finally:
        # Cleanup: Delete file to save space on Render
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Cleaned up: {file_path}")
