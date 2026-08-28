"""Modul route untuk pengenalan wajah (Face Verification) dan pendaftaran wajah baru (Face Capture)."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from src.config import RATE_LIMIT_FACE, logger
from src.core.security import require_api_key, limiter
from src.models.schemas import FaceVerifyRequest, FaceCaptureRequest
from src.services.face_service import face_service

# Inisialisasi router dengan tag Face Recognition
router = APIRouter(tags=["Face Recognition"])


@router.post("/verify-face", dependencies=[Depends(require_api_key)])
@limiter.limit(RATE_LIMIT_FACE)
async def verify_face(request: Request, response: Response, face_request: FaceVerifyRequest):
    """Memverifikasi identitas wajah dari gambar Base64 terhadap seluruh wajah yang telah terdaftar.

    Args:
        request (Request): Objek request HTTP.
        response (Response): Objek response HTTP.
        face_request (FaceVerifyRequest): Payload berisi data gambar berformat Base64.

    Returns:
        dict: Hasil verifikasi berupa status 'success' beserta nama orang yang teridentifikasi,
              atau status 'error' jika wajah tidak terdeteksi / tidak cocok.

    Raises:
        HTTPException: Status 500 jika terjadi kegagalan pemrosesan komputasi wajah.
    """
    try:
        matched_name = await face_service.verify_face(face_request.face_encoding)

        if matched_name is None:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Wajah tidak terdeteksi atau tidak dikenali!"},
            )

        return {"status": "success", "name": matched_name}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capture-face", dependencies=[Depends(require_api_key)])
@limiter.limit(RATE_LIMIT_FACE)
async def capture_face(request: Request, response: Response, capture_request: FaceCaptureRequest):
    """Mendaftarkan wajah baru ke dalam sistem (menyimpan file gambar ke disk dan mengindeks encoding ke RAM).

    Args:
        request (Request): Objek request HTTP.
        response (Response): Objek response HTTP.
        capture_request (FaceCaptureRequest): Payload berisi nama orang/siswa dan string gambar Base64.

    Returns:
        dict: Konfirmasi status registrasi sukses beserta nama yang didaftarkan dan nama file gambar yang disimpan.

    Raises:
        HTTPException: Status 400 jika nama tidak valid atau tidak ada wajah yang terdeteksi pada gambar.
        HTTPException: Status 500 jika terjadi kesalahan sistem.
    """
    try:
        name, filename = await face_service.capture_face(capture_request.name, capture_request.face_encoding)
        return {"status": "success", "name": name, "file": filename}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face capture error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
