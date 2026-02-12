import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def download_audio(youtube_url: str, output_path: str = "temp_audio") -> dict:
    """Downloads audio and extracts Global Metadata for any video."""
    clean_url = youtube_url.split(
        "?")[0] if "youtu.be" in youtube_url else youtube_url.split("&")[0]

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    cookie_file = os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), 'cookies.txt')

    ydl_opts = {
        'format': '140/251/139/bestaudio/best',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
        'allow_unsecure_ejs': True,
        'extractor_args': {'youtube': {'remote_components': 'ejs:github', 'player_client': ['android', 'ios', 'web']}},
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            video_id = info['id']
            return {
                "audio_path": os.path.join(output_path, f"{video_id}.mp3"),
                "title": info.get('title', ''),
                "description": info.get('description', ''),
                "video_id": video_id
            }
    except Exception as e:
        raise e


def transcribe_audio(file_path: str) -> str:
    """Automatic Language Detection with quality prompt."""
    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                model="whisper-large-v3",
                prompt="Transcribe accurately. Maintain original language and technical terms.",
                response_format="json"
            )
        return transcription.text
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
