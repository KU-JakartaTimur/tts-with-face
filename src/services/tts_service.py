"""Modul layanan Text-to-Speech (Edge TTS) dan utilitas manajemen file audio."""

import os
from datetime import datetime
from src.config import (
    INDONESIAN_VOICES,
    ENGLISH_VOICES,
    OUTPUT_DIR,
    CLEANUP_INTERVAL,
    logger,
)


def estimate_duration(text: str, language: str = "indonesian") -> float:
    """Memperkirakan panjang durasi ucapan audio berdasarkan jumlah kata dan bahasa teks.

    Menggunakan asumsi rata-rata kecepatan bicara:
    - Bahasa Indonesia: ~120 kata per menit
    - Bahasa Inggris: ~150 kata per menit

    Args:
        text (str): Teks yang akan diucapkan.
        language (str, optional): Bahasa teks ('indonesian' atau 'english'). Default 'indonesian'.

    Returns:
        float: Estimasi durasi dalam satuan detik (dibulatkan 2 desimal).
    """
    word_count = len(text.split())
    words_per_minute = 120 if language.lower() == "indonesian" else 150
    duration_minutes = word_count / words_per_minute
    return round(duration_minutes * 60, 2)


def get_voice_name(voice: str, language: str) -> str:
    """Mengambil nama resmi model suara Edge TTS berdasarkan ID suara dan bahasa.

    Args:
        voice (str): ID suara yang dipilih (cth: 'female', 'male', 'female_us', 'male_us').
        language (str): Bahasa teks ('indonesian' atau 'english').

    Returns:
        str: Nama lengkap model neural voice Edge TTS (cth: 'id-ID-GadisNeural', 'en-US-AriaNeural').
    """
    if language.lower() == "english":
        return ENGLISH_VOICES.get(voice, ENGLISH_VOICES["female_us"])["name"]
    else:
        return INDONESIAN_VOICES.get(voice, INDONESIAN_VOICES["female"])["name"]


async def cleanup_old_files() -> None:
    """Menghapus file audio hasil sintesis yang usianya melebihi batas waktu CLEANUP_INTERVAL.

    Dijalankan sebagai Background Task di FastAPI setelah proses pembuatan audio selesai
    untuk mencegah penumpukan file audio di direktori output server.
    """
    try:
        current_time = datetime.now().timestamp()
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path) and filename.endswith((".wav", ".mp3")):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > CLEANUP_INTERVAL:
                    os.remove(file_path)
                    logger.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")
