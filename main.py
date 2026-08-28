"""Titik masuk utama (entry point) aplikasi ARSA Technology TTS with Face Recognition.

Menjalankan server web ASGI Uvicorn pada port 8021 menggunakan konfigurasi aplikasi dari src.app.
"""

import uvicorn
from src.app import app

if __name__ == "__main__":
    # Menjalankan server uvicorn pada host 0.0.0.0 dan port 8021
    uvicorn.run(app, host="0.0.0.0", port=8021)