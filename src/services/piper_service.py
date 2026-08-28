"""Modul layanan Piper TTS (Local Offline Neural Text-to-Speech Engine).

Menyediakan fungsionalitas pemuatan model ONNX Piper ke memori cache dan sintesis audio
ke format WAV secara offline tanpa koneksi internet.
"""

import os
import wave
from fastapi import HTTPException
from src.config import (
    PIPER_AVAILABLE,
    PIPER_VOICES_DIR,
    PIPER_VOICES,
    PIPER_DEFAULT_VOICE,
    PiperVoice,
    logger,
)

# Cache in-memory untuk objek PiperVoice (pemuatan model ONNX membutuhkan resource tinggi, sehingga di-cache)
_piper_voice_cache: dict = {}

if PIPER_AVAILABLE:
    logger.info(f"Piper TTS engine AVAILABLE (voices dir: {PIPER_VOICES_DIR}, {len(PIPER_VOICES)} voice(s) mapped)")
else:
    logger.warning("Piper TTS engine NOT available — install 'piper-tts' to enable the local engine")


def get_piper_voice(voice: str) -> "PiperVoice":
    """Memuat dan menyimpan ke dalam cache objek model suara Piper berdasarkan ID suara.

    Args:
        voice (str): ID suara ramah pengguna (cth: 'en_female', 'en_male', 'id_female').

    Returns:
        PiperVoice: Instance model suara Piper yang siap digunakan untuk sintesis.

    Raises:
        HTTPException: Status 503 jika pustaka `piper-tts` belum terinstall.
        HTTPException: Status 400 jika ID suara tidak dikenal dalam konfigurasi PIPER_VOICES.
        HTTPException: Status 503 jika file model .onnx tidak ditemukan pada disk.
    """
    if not PIPER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Piper TTS engine is not installed. Run 'pip install piper-tts'.",
        )

    model_name = PIPER_VOICES.get(voice, PIPER_VOICES.get(PIPER_DEFAULT_VOICE))
    if model_name is None:
        raise HTTPException(status_code=400, detail=f"Unknown Piper voice '{voice}'.")

    # Kembalikan dari cache jika model sudah pernah dimuat
    if model_name in _piper_voice_cache:
        return _piper_voice_cache[model_name]

    model_path = os.path.join(PIPER_VOICES_DIR, f"{model_name}.onnx")
    config_path = f"{model_path}.json"
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=503,
            detail=(
                f"Piper voice model '{model_name}.onnx' not found in {PIPER_VOICES_DIR}. "
                "Download it from https://huggingface.co/rhasspy/piper-voices"
            ),
        )

    config_arg = config_path if os.path.exists(config_path) else None
    loaded = PiperVoice.load(model_path, config_path=config_arg)
    _piper_voice_cache[model_name] = loaded
    logger.info(f"Loaded Piper voice model: {model_name}")
    return loaded


def synthesize_piper(text: str, voice: str, output_file: str) -> None:
    """Melakukan sintesis ucapan menggunakan engine Piper TTS ke dalam file format WAV.

    Catatan: Proses ini bersifat CPU-bound/blocking, sehingga sebaiknya dipanggil
    menggunakan `asyncio.to_thread` di dalam async route.

    Args:
        text (str): Teks yang akan disintesis menjadi suara.
        voice (str): ID suara Piper yang digunakan.
        output_file (str): Lokasi file path absolut/relatif tempat menyimpan output WAV.
    """
    piper_voice = get_piper_voice(voice)
    with wave.open(output_file, "wb") as wav_file:
        if hasattr(piper_voice, "synthesize_wav"):
            piper_voice.synthesize_wav(text, wav_file)
        else:
            piper_voice.synthesize(text, wav_file)
