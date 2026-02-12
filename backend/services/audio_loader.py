import os
from groq import Groq
from pytubefix import YouTube  # 👇 New Hero Library
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def download_audio(url: str):
    print(f"⬇️ Downloading with Pytubefix: {url}")

    try:
        # Pytubefix automatically handles 'Sign in' & 'Bot' checks
        yt = YouTube(url)

        # 'get_lowest_resolution' hamesha single MP4 file deta hai (No FFmpeg needed)
        # Ye sabse safe method hai Render free tier ke liye
        stream = yt.streams.get_lowest_resolution()

        # Download
        filename = stream.download(output_path="temp_audio")

        # Rename file to simple ID format (Optional but good for cleanliness)
        new_filename = f"temp_audio/{yt.video_id}.mp4"
        if os.path.exists(new_filename):
            os.remove(new_filename)
        os.rename(filename, new_filename)

        return new_filename, yt.title

    except Exception as e:
        print(f"❌ Download Error: {e}")
        # Error message saaf dikhega
        raise Exception(f"Download Failed: {str(e)}")


def transcribe_audio(file_path: str):
    print(f"🚀 Transcribing: {file_path}")

    try:
        with open(file_path, "rb") as file:
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
