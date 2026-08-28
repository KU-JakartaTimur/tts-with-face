"""Modul keamanan dan pembatasan laju permintaan (Rate Limiting & Authentication).

Menyediakan fungsi autentikasi API Key berbasis header dan pembuatan key rate limit
berdasarkan API Key atau remote IP address.
"""

import secrets
from typing import Optional
from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import (
    API_KEYS,
    API_KEY_HEADER_NAME,
    AUTH_ENABLED,
    RATE_LIMIT_DEFAULT,
    RATE_LIMIT_STORAGE_URI,
    logger,
)


def rate_limit_key(request: Request) -> str:
    """Menentukan kunci identifikasi untuk bucket rate limiter per request.

    Jika header API Key dikirimkan pada request, kunci akan memakai API Key tersebut.
    Jika tidak ada API Key, kunci akan memakai alamat IP klien. Hal ini mencegah
    seorang pengguna menghabiskan kuota pengguna lain yang berbagi IP publik yang sama.

    Args:
        request (Request): Objek request HTTP dari FastAPI/Starlette.

    Returns:
        str: String identifier unik untuk rate limit bucket (cth: 'key:xxx' atau 'ip:127.0.0.1').
    """
    key = request.headers.get(API_KEY_HEADER_NAME)
    if key:
        return f"key:{key}"
    return f"ip:{get_remote_address(request)}"


# Inisialisasi instance limiter global
limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[RATE_LIMIT_DEFAULT],
    storage_uri=RATE_LIMIT_STORAGE_URI,
    headers_enabled=True,
)

# Definisi skema security APIKeyHeader
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


async def require_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """Dependency FastAPI untuk memvalidasi API Key pada header HTTP.

    Jika AUTH_ENABLED bernilai False (mode development tanpa konfigurasi API_KEY),
    fungsi ini akan langsung meloloskan request. Jika aktif, akan melakukan verifikasi
    konstanta waktu (constant-time comparison) untuk mencegah timing attack.

    Args:
        api_key (Optional[str]): Nilai API Key dari request header.

    Returns:
        Optional[str]: API Key yang valid jika autentikasi berhasil, atau None jika dinonaktifkan.

    Raises:
        HTTPException: Status 401 jika API Key tidak disertakan saat auth aktif.
        HTTPException: Status 403 jika API Key yang diberikan tidak cocok dengan daftar yang valid.
    """
    if not AUTH_ENABLED:
        return None
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing API key. Provide it via '{API_KEY_HEADER_NAME}' header.",
        )
    # Perbandingan waktu konstan terhadap setiap kunci yang valid untuk mencegah kebocoran waktu
    if not any(secrets.compare_digest(api_key, valid) for valid in API_KEYS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return api_key
