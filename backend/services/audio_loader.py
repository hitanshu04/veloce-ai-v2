import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def download_audio(url: str):
    print(f"⬇️ Downloading Audio (No FFmpeg): {url}")

    # 👇 CHANGES: FFmpeg hataya. Best raw audio download karenge (m4a/webm)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',  # Extension dynamic hogi
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            ext = info['ext']  # File extension pata lagao
            filename = f"temp_audio/{video_id}.{ext}"

            return filename, info.get('title', 'Unknown Video')
    except Exception as e:
        print(f"❌ Download Error: {e}")
        raise Exception(f"Download failed: {str(e)}")


def transcribe_audio(file_path: str):
    print(f"🚀 Transcribing Raw Audio: {file_path}")

    try:
        with open(file_path, "rb") as file:
            # Groq m4a/webm sab samajhta hai. No conversion needed!
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json",
                temperature=0.0
            )

        print("✅ Transcription Complete!")
        return transcription.text

    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        raise Exception("Transcription failed via Groq API.")
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Cleaned up: {file_path}")
