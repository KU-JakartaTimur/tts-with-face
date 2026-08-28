"""Modul route untuk sintesis Text-to-Speech (TTS) tunggal, batch, daftar suara, dan unduhan file audio."""

import os
import uuid
import asyncio
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse
import edge_tts

from src.config import (
    INDONESIAN_VOICES,
    ENGLISH_VOICES,
    PIPER_VOICES,
    PIPER_DEFAULT_VOICE,
    OUTPUT_DIR,
    MAX_TEXT_LENGTH,
    RATE_LIMIT_TTS,
    RATE_LIMIT_TTS_BATCH,
    RATE_LIMIT_AUDIO,
    logger,
)
from src.core.security import require_api_key, limiter
from src.models.schemas import TTSRequest, TTSResponse, VoiceInfo
from src.services.piper_service import synthesize_piper
from src.services.tts_service import estimate_duration, get_voice_name, cleanup_old_files

# Inisialisasi router dengan tag TTS
router = APIRouter(tags=["TTS"])


@router.get("/voices", response_model=List[VoiceInfo])
async def list_voices():
    """Mengambil seluruh daftar model suara yang tersedia di sistem (Edge TTS online & Piper offline).

    Returns:
        List[VoiceInfo]: Daftar profil suara lengkap dengan ID suara, bahasa, deskripsi, dan engine.
    """
    voices = []

    # Suara Bahasa Indonesia (Edge TTS)
    for voice_id, voice_data in INDONESIAN_VOICES.items():
        voices.append(VoiceInfo(
            voice_id=voice_id,
            name=voice_data["name"],
            gender=voice_data["gender"],
            description=voice_data["description"],
            language="Indonesian",
        ))

    # Suara Bahasa Inggris (Edge TTS)
    for voice_id, voice_data in ENGLISH_VOICES.items():
        voices.append(VoiceInfo(
            voice_id=voice_id,
            name=voice_data["name"],
            gender=voice_data["gender"],
            description=voice_data["description"],
            language="English",
        ))

    # Suara Piper Neural Offline
    for voice_id, model_name in PIPER_VOICES.items():
        voices.append(VoiceInfo(
            voice_id=voice_id,
            name=model_name,
            gender="Unknown",
            description=f"Local Piper neural voice ({model_name})",
            language="Indonesian" if voice_id.startswith("id") else "English",
            engine="piper",
        ))

    return voices


@router.post("/tts", response_model=TTSResponse, dependencies=[Depends(require_api_key)])
@limiter.limit(RATE_LIMIT_TTS)
async def generate_speech(
    request: Request,
    response: Response,
    tts_request: TTSRequest,
    background_tasks: BackgroundTasks,
):
    """Menghasilkan file audio ucapan dari teks input (Text-to-Speech).

    Mendukung engine online Microsoft Edge TTS maupun engine offline Piper TTS.
    Menghasilkan file berformat WAV/MP3 di server dan mendaftarkan pembersihan file via Background Tasks.

    Args:
        request (Request): Objek request HTTP untuk kalkulasi rate limiter.
        response (Response): Objek response HTTP.
        tts_request (TTSRequest): Parameter payload berisi teks, suara, nada, kecepatan bicara, dan format output.
        background_tasks (BackgroundTasks): Handler untuk mendaftarkan tugas pembersihan file lama di latar belakang.

    Returns:
        TTSResponse: Metadata respons audio (audio_id, URL unduhan, estimasi durasi, dan ukuran file).

    Raises:
        HTTPException: Status 400 jika teks kosong atau melebihi MAX_TEXT_LENGTH.
        HTTPException: Status 500 jika proses sintesis gagal membuat file.
    """
    try:
        # Validasi input teks
        if not tts_request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(tts_request.text) > MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Text too long (max {MAX_TEXT_LENGTH} characters)",
            )

        engine = tts_request.engine.lower()

        # Generate UUID unik untuk file audio ini
        audio_id = str(uuid.uuid4())

        if engine == "piper":
            # Piper TTS memproses secara lokal dan menghasilkan file WAV
            voice_name = PIPER_VOICES.get(tts_request.voice, PIPER_VOICES.get(PIPER_DEFAULT_VOICE, tts_request.voice))
            filename = f"{audio_id}.wav"
            output_file = os.path.join(OUTPUT_DIR, filename)
            # Proses sintesis CPU-bound dipindahkan dari event loop utama
            await asyncio.to_thread(synthesize_piper, tts_request.text, tts_request.voice, output_file)
        else:
            # Edge TTS online
            voice_name = get_voice_name(tts_request.voice, tts_request.language)

            file_extension = "wav" if tts_request.output_format.lower() == "wav" else "mp3"
            filename = f"{audio_id}.{file_extension}"
            output_file = os.path.join(OUTPUT_DIR, filename)

            # Inisialisasi objek Communicate dari edge_tts
            communicate = edge_tts.Communicate(
                text=tts_request.text,
                voice=voice_name,
                rate=tts_request.rate,
                pitch=tts_request.pitch,
                volume=tts_request.volume,
            )

            # Simpan file audio secara asynchronous
            await communicate.save(output_file)

        # Verifikasi bahwa file berhasil dibuat di disk
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Failed to generate audio file")

        # Mengambil ukuran file
        file_size = os.path.getsize(output_file)

        # Estimasi durasi ucapan
        duration = estimate_duration(tts_request.text, tts_request.language)

        # Jadwalkan pembersihan file audio yang sudah usang di latar belakang
        background_tasks.add_task(cleanup_old_files)

        logger.info(f"Generated audio: {audio_id} for voice: {voice_name}, size: {file_size} bytes")

        return TTSResponse(
            success=True,
            message="Audio generated successfully",
            audio_id=audio_id,
            audio_url=f"/audio/{audio_id}",
            duration_estimate=duration,
            voice_used=voice_name,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")


@router.get("/audio/{audio_id}", dependencies=[Depends(require_api_key)])
@limiter.limit(RATE_LIMIT_AUDIO)
async def download_audio(request: Request, response: Response, audio_id: str):
    """Mengunduh file audio hasil sintesis berdasarkan `audio_id`.

    Mencari file berformat .wav atau .mp3 yang sesuai dengan identifier `audio_id` pada direktori penyimpanan.

    Args:
        request (Request): Objek request HTTP.
        response (Response): Objek response HTTP.
        audio_id (str): UUID file audio yang ingin diunduh.

    Returns:
        FileResponse: Respons stream file binary audio (audio/wav atau audio/mpeg).

    Raises:
        HTTPException: Status 404 jika file audio tidak ditemukan.
        HTTPException: Status 500 jika terjadi kesalahan sistem saat mengunduh.
    """
    try:
        for ext, media_type in (("wav", "audio/wav"), ("mp3", "audio/mpeg")):
            file_path = os.path.join(OUTPUT_DIR, f"{audio_id}.{ext}")
            if os.path.exists(file_path):
                return FileResponse(
                    file_path,
                    media_type=media_type,
                    filename=f"arsa_tts_{audio_id}.{ext}",
                )

        raise HTTPException(status_code=404, detail="Audio file not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download audio")


@router.post("/tts/batch", dependencies=[Depends(require_api_key)])
@limiter.limit(RATE_LIMIT_TTS_BATCH)
async def generate_batch_speech(
    request: Request,
    response: Response,
    requests: List[TTSRequest],
    background_tasks: BackgroundTasks,
):
    """Menghasilkan beberapa file audio secara batch dalam satu permintaan HTTP (maksimal 10 item per batch).

    Args:
        request (Request): Objek request HTTP.
        response (Response): Objek response HTTP.
        requests (List[TTSRequest]): List objek parameter TTS yang akan diproses secara berurutan.
        background_tasks (BackgroundTasks): Handler tugas latar belakang pembersihan file.

    Returns:
        dict: Ringkasan hasil pemrosesan batch (total, jumlah sukses, jumlah gagal, dan detail hasil tiap item).

    Raises:
        HTTPException: Status 400 jika jumlah item dalam batch lebih dari 10.
        HTTPException: Status 500 jika terjadi error tak tertangani.
    """
    try:
        if len(requests) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 requests per batch")

        results = []

        for req in requests:
            try:
                audio_id = str(uuid.uuid4())
                engine = req.engine.lower()

                if engine == "piper":
                    voice_name = PIPER_VOICES.get(req.voice, PIPER_VOICES.get(PIPER_DEFAULT_VOICE, req.voice))
                    filename = f"{audio_id}.wav"
                    output_file = os.path.join(OUTPUT_DIR, filename)
                    await asyncio.to_thread(synthesize_piper, req.text, req.voice, output_file)
                else:
                    voice_name = get_voice_name(req.voice, req.language)

                    file_extension = "wav" if req.output_format.lower() == "wav" else "mp3"
                    filename = f"{audio_id}.{file_extension}"
                    output_file = os.path.join(OUTPUT_DIR, filename)

                    communicate = edge_tts.Communicate(
                        text=req.text,
                        voice=voice_name,
                        rate=req.rate,
                        pitch=req.pitch,
                        volume=req.volume,
                    )

                    await communicate.save(output_file)

                file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
                duration = estimate_duration(req.text, req.language)

                results.append({
                    "success": True,
                    "audio_id": audio_id,
                    "audio_url": f"/audio/{audio_id}",
                    "duration_estimate": duration,
                    "voice_used": voice_name,
                    "file_size": file_size,
                    "text_preview": req.text[:50] + "..." if len(req.text) > 50 else req.text,
                })

            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "text_preview": req.text[:50] + "..." if len(req.text) > 50 else req.text,
                })

        background_tasks.add_task(cleanup_old_files)

        return {
            "batch_success": True,
            "total_requests": len(requests),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")
