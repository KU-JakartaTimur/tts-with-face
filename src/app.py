"""Modul inisialisasi aplikasi FastAPI.

Mengonfigurasi aplikasi FastAPI utama, menyusun middleware (CORS & SlowAPI rate limiting),
menambahkan exception handler, dan mendaftarkan router endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.core.security import limiter
from src.routers.general import router as general_router
from src.routers.tts import router as tts_router
from src.routers.face import router as face_router


def create_app() -> FastAPI:
    """Membuat dan mengonfigurasi instance aplikasi FastAPI.

    Returns:
        FastAPI: Objek aplikasi FastAPI yang siap dijalankan oleh server ASGI (seperti Uvicorn).
    """
    app = FastAPI(
        title="ARSA Technology - Edge TTS API ~ Modified By mdestafadilah",
        description="Indonesian Text-to-Speech API using Microsoft Edge TTS & Face Recognition",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware CORS untuk mengizinkan request cross-origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Menghubungkan state rate limiter dan middleware slowapi
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Mendaftarkan router endpoint aplikasi
    app.include_router(general_router)
    app.include_router(tts_router)
    app.include_router(face_router)

    return app


# Instance aplikasi global untuk uvicorn ASGI runner
app = create_app()
