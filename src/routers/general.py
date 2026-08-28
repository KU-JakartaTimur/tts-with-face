"""Modul route untuk informasi umum, status layanan (health), dan statistik server."""

import os
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Response, HTTPException

from src.config import (
    OUTPUT_DIR,
    AUTH_ENABLED,
    PIPER_AVAILABLE,
    ALL_VOICES,
    MAX_TEXT_LENGTH,
    CLEANUP_INTERVAL,
    RATE_LIMIT_STATS,
    logger,
)
from src.core.security import require_api_key, limiter

# Inisialisasi router dengan tag General
router = APIRouter(tags=["General"])


@router.get("/")
async def root():
    """Endpoint root yang menyediakan informasi ringkas service dan daftar endpoint yang tersedia.

    Returns:
        dict: Metadata informasi service, status operasional, dan daftar endpoint.
    """
    return {
        "service": "ARSA Technology Edge-TTS API",
        "version": "1.0.0",
        "status": "running",
        "supported_languages": ["Indonesian", "English"],
        "endpoints": {
            "tts": "/tts - Generate speech",
            "voices": "/voices - List available voices",
            "health": "/health - Health check",
            "stats": "/stats - Service statistics",
            "audio": "/audio/{audio_id} - Download audio",
            "verify_face": "/verify-face - Verify a face against registered faces",
            "capture_face": "/capture-face - Register a new face",
            "docs": "/docs - API documentation",
        },
    }


@router.get("/health")
async def health_check():
    """Endpoint health check untuk memantau status kesiapan server (liveness/readiness probe).

    Returns:
        dict: Informasi status sistem, timestamp UTC/lokal, ketersediaan direktori penyimpanan,
              status autentikasi, serta engine TTS yang aktif.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "edge-tts-api",
        "output_dir_writable": os.access(OUTPUT_DIR, os.W_OK),
        "auth_enabled": AUTH_ENABLED,
        "engines": {
            "edge": True,
            "piper": PIPER_AVAILABLE,
        },
    }


@router.get("/stats", dependencies=[Depends(require_api_key)])
@limiter.limit(RATE_LIMIT_STATS)
async def get_stats(request: Request, response: Response):
    """Endpoint untuk mengambil ringkasan statistik penggunaan penyimpanan dan konfigurasi server.

    Memerlukan autentikasi API Key jika `AUTH_ENABLED` bernilai True.

    Args:
        request (Request): Objek request HTTP.
        response (Response): Objek response HTTP.

    Returns:
        dict: Data statistik mencakup jumlah file audio aktif, total ukuran file (bytes dan MB),
              jumlah model suara tersedia, dan interval pembersihan berkala.

    Raises:
        HTTPException: Status 500 jika terjadi kegagalan pembacaan folder output.
    """
    try:
        # Menghitung file audio pada direktori output
        files = os.listdir(OUTPUT_DIR) if os.path.exists(OUTPUT_DIR) else []
        audio_files = [f for f in files if f.endswith((".wav", ".mp3"))]

        # Menghitung total ukuran file audio
        total_size = 0
        for f in audio_files:
            file_path = os.path.join(OUTPUT_DIR, f)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)

        return {
            "total_audio_files": len(audio_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "available_voices": len(ALL_VOICES),
            "supported_languages": ["Indonesian", "English"],
            "max_text_length": MAX_TEXT_LENGTH,
            "cleanup_interval_hours": CLEANUP_INTERVAL / 3600,
            "output_directory": OUTPUT_DIR,
        }

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
