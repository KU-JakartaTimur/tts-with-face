"""Modul konfigurasi utama aplikasi.

Mengelola variabel lingkungan (environment variables), direktori kerja,
daftar model suara (Edge TTS dan Piper TTS), serta pengaturan keamanan dan rate limiting.
"""

import os
import logging
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Import opsional engine Piper TTS (neural offline)
try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    try:
        # Untuk rilis lama piper-tts
        from piper.voice import PiperVoice
        PIPER_AVAILABLE = True
    except ImportError:
        PiperVoice = None
        PIPER_AVAILABLE = False

# Konfigurasi logging aplikasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ttswithface")

# Konfigurasi direktori output dan batas teks
OUTPUT_DIR = str(os.getenv("OUTPUT_DIR", "./app/output"))
MAX_TEXT_LENGTH = int(os.getenv("TTS_MAX_TEXT_LENGTH", "5000"))
CLEANUP_INTERVAL = int(os.getenv("TTS_CLEANUP_INTERVAL", "3600"))

# Konfigurasi pengenalan wajah (Face Recognition)
KNOWN_FACES_DIR = str(os.getenv("KNOWN_FACES_DIR", "./app/faces"))
FACE_ALLOWED_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# Konfigurasi Autentikasi API Key
API_KEYS = {k.strip() for k in os.getenv("API_KEYS", os.getenv("API_KEY", "")).split(",") if k.strip()}
API_KEY_HEADER_NAME = os.getenv("API_KEY_HEADER", "X-API-Key")
AUTH_ENABLED = len(API_KEYS) > 0

if AUTH_ENABLED:
    logger.info(f"API key authentication ENABLED ({len(API_KEYS)} key(s) loaded, header: {API_KEY_HEADER_NAME})")
else:
    logger.warning("API key authentication DISABLED — set API_KEY or API_KEYS env var to enable for production")

# Konfigurasi Rate Limiting
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
RATE_LIMIT_TTS = os.getenv("RATE_LIMIT_TTS", "30/minute")
RATE_LIMIT_TTS_BATCH = os.getenv("RATE_LIMIT_TTS_BATCH", "5/minute")
RATE_LIMIT_AUDIO = os.getenv("RATE_LIMIT_AUDIO", "120/minute")
RATE_LIMIT_STATS = os.getenv("RATE_LIMIT_STATS", "30/minute")
RATE_LIMIT_FACE = os.getenv("RATE_LIMIT_FACE", "30/minute")
RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

# Daftar konfigurasi suara Bahasa Indonesia (Edge TTS)
INDONESIAN_VOICES = {
    "female": {
        "name": "id-ID-GadisNeural",
        "gender": "Female",
        "description": "Natural Indonesian female voice - Professional"
    },
    "male": {
        "name": "id-ID-ArdiNeural", 
        "gender": "Male",
        "description": "Natural Indonesian male voice - Authoritative"
    }
}

# Daftar konfigurasi suara Bahasa Inggris (Edge TTS)
ENGLISH_VOICES = {
    "female_us": {
        "name": "en-US-AriaNeural",
        "gender": "Female",
        "description": "Natural US English female voice"
    },
    "male_us": {
        "name": "en-US-GuyNeural",
        "gender": "Male",
        "description": "Natural US English male voice"
    }
}

ALL_VOICES = {**INDONESIAN_VOICES, **ENGLISH_VOICES}

# Konfigurasi direktori dan mapping model Piper TTS
PIPER_VOICES_DIR = str(os.getenv("PIPER_VOICES_DIR", "./app/piper_voices"))

PIPER_VOICES = {
    "id_female": "id_ID-female-medium",
    "en_female": "en_US-lessac-medium",
    "en_male": "en_US-ryan-medium",
}
_piper_env = os.getenv("PIPER_VOICES", "").strip()
if _piper_env:
    for pair in _piper_env.split(","):
        if "=" in pair:
            vid, model = pair.split("=", 1)
            PIPER_VOICES[vid.strip()] = model.strip()

PIPER_DEFAULT_VOICE = os.getenv("PIPER_DEFAULT_VOICE", "en_female")

SUPPORTED_ENGINES = {"edge", "piper"}
DEFAULT_ENGINE = os.getenv("TTS_DEFAULT_ENGINE", "edge").strip().lower()
if DEFAULT_ENGINE not in SUPPORTED_ENGINES:
    logger.warning(
        f"TTS_DEFAULT_ENGINE='{DEFAULT_ENGINE}' is not one of {sorted(SUPPORTED_ENGINES)}; falling back to 'edge'"
    )
    DEFAULT_ENGINE = "edge"

# Memastikan direktori yang dibutuhkan telah dibuat
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
