import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def download_audio(url: str):
    print(f"⬇️ 2026 Browser-Impersonation Mode: {url}")
    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/best',
        'outtmpl': 'temp_audio/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # 👇 NEW 2026 BYPASS: Impersonate a real Chrome session
        'impersonate_base_headers': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        },
        # Cookies are still your strongest ID card
        'cookiefile': 'cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info), info.get('title', 'Video')
    except Exception as e:
        print(f"❌ Blocked: {e}")
        # If this fails, we will use a pre-processed dataset for your portfolio demo
        raise Exception(
            "YouTube Security Block. Please try a different video.")
