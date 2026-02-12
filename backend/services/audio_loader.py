import os
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")


def get_video_id(url):
    """ Helper to clean video ID from URL """
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None


def download_audio(url: str):
    """
    AB HUM AUDIO DOWNLOAD NAHI KARENGE.
    Hum seedha Youtube se likha hua text (Captions) uthayenge.
    """
    print(f"⬇️ Fetching Transcript (No Download): {url}")

    video_id = get_video_id(url)
    if not video_id:
        raise Exception("Invalid YouTube URL")

    try:
        # 1. Direct Text Fetching (Super Fast ⚡)
        # Hum cookies use karenge taaki bot detection bypass ho
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, cookies='cookies.txt')

        # 2. Text ko jod kar ek string banao
        full_text = " ".join([entry['text'] for entry in transcript_list])

        # 3. Fake "Audio File" banao (Text file save karo)
        # Taaki humara agla function isey padh sake
        filename = f"temp_audio/{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_text)

        print("✅ Transcript Fetched Successfully!")
        return filename, "YouTube Video (Transcript)"

    except Exception as e:
        print(f"❌ Transcript Error: {e}")
        # Agar Captions nahi mile, toh user ko bata do
        raise Exception(
            f"Could not fetch captions. Video might not have subtitles. Error: {str(e)}")


def transcribe_audio(file_path: str):
    """
    Ye function ab Groq use nahi karega agar file .txt hai.
    Seedha text padh ke wapas de dega.
    """
    print(f"🚀 Reading Transcript: {file_path}")

    try:
        # Agar humne text file bheji hai, toh bas read kar lo
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        # (Future Proofing) Agar kabhi audio file aayi toh Groq use hoga
        # ... lekin abhi hum sirf text bhej rahe hain.
        return "No content found."

    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🗑️ Cleanup Done")
