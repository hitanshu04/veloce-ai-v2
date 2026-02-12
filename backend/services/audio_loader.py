import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def download_audio(url: str):
    print(f"⬇️ Downloading Smart Audio (Auto-Format): {url}")

    ydl_opts = {
        # 👇 CHANGE: Sirf 'worst' likha hai.
        # Matlab: "Sabse chhota file do, chahe wo MP4 ho ya WEBM".
        # Ye Render par 100% chalega bina FFmpeg ke.
        'format': 'worst',
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            ext = info['ext']
            filename = f"temp_audio/{video_id}.{ext}"
            return filename, info.get('title', 'Unknown Video')
    except Exception as e:
        print(f"❌ Download Error: {e}")
        raise Exception(f"YouTube Download Failed: {str(e)}")


def transcribe_audio(file_path: str):
    print(f"🚀 Transcribing File: {file_path}")

    try:
        with open(file_path, "rb") as file:
            # Groq apne aap extension detect kar lega (mp4/webm/m4a)
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
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🗑️ Cleanup Done")
