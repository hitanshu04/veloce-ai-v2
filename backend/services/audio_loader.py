import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def download_audio(url: str):
    print(f"⬇️ Starting Audio Download (Pytubefix): {url}")

    try:
        # 1. Initialize YouTube Object with fixes
        # 'use_oauth=False' aur 'allow_oauth_cache=True' bot detection kam karta hai
        yt = YouTube(url, on_progress_callback=on_progress)

        print(f"🔍 Video Found: {yt.title}")

        # 2. Get Audio Stream (M4A is best for Whisper)
        # Ye bina FFmpeg ke chalta hai
        ys = yt.streams.get_audio_only()

        if not ys:
            raise Exception("No audio stream found.")

        # 3. Download
        print("📥 Downloading stream...")
        filename = ys.download(output_path="temp_audio")

        # 4. Rename to simple ID (Safety)
        new_filename = f"temp_audio/{yt.video_id}.m4a"
        if os.path.exists(new_filename):
            os.remove(new_filename)
        os.rename(filename, new_filename)

        print(f"✅ Download Complete: {new_filename}")
        return new_filename, yt.title

    except Exception as e:
        print(f"❌ Audio Download Error: {e}")
        # Agar Pytubefix bhi fail hua, tabhi error denge.
        raise Exception(f"Failed to download audio. Reason: {str(e)}")


def transcribe_audio(file_path: str):
    print(f"🚀 Sending Audio to Groq Whisper: {file_path}")

    try:
        with open(file_path, "rb") as file:
            # Whisper Large V3 - The Best Speech-to-Text
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json",
                temperature=0.0
            )
        print("✅ Transcription Success!")
        return transcription.text

    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        raise Exception(f"Transcription failed: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🗑️ Cleanup Done")
