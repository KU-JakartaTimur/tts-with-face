"""Modul layanan pengenalan wajah (Face Recognition Service).

Menyediakan fungsi dekode gambar Base64, ekstraksi fitur wajah (face encodings),
indeks wajah terdaftar di memori, verifikasi wajah terhadap database, dan registrasi wajah baru.
"""

import os
import re
import base64
import asyncio
from typing import Optional, List, Tuple
import numpy as np
import cv2
import face_recognition
from fastapi import HTTPException

from src.config import KNOWN_FACES_DIR, FACE_ALLOWED_EXT, logger


def decode_base64_image(raw: str) -> np.ndarray:
    """Mendekode string gambar Base64 (dengan atau tanpa prefix data URI) menjadi array gambar BGR OpenCV.

    Args:
        raw (str): String gambar format Base64 (cth: 'data:image/jpeg;base64,...' atau raw base64).

    Returns:
        np.ndarray: Objek gambar OpenCV dalam format array NumPy BGR.

    Raises:
        HTTPException: Status 400 jika string base64 rusak atau format gambar tidak dapat diproses oleh OpenCV.
    """
    b64_data = raw.split(",", 1)[1] if "," in raw else raw
    try:
        img_bytes = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 gambar tidak valid!")
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Gambar tidak dapat diproses!")
    return img


class FaceRecognitionService:
    """Kelas pengelola (manager) pengenalan dan registrasi wajah.

    Mengelola daftar encoding wajah dan nama yang dimuat ke dalam memori RAM
    dari folder gambar `KNOWN_FACES_DIR` saat aplikasi diinisialisasi.

    Attributes:
        faces_dir (str): Direktori penyimpanan gambar wajah yang terdaftar.
        known_face_encodings (List[np.ndarray]): List vektor embedding wajah 128 dimensi.
        known_face_names (List[str]): List nama orang/siswa yang sesuai dengan urutan encodings.
    """

    def __init__(self, faces_dir: str = KNOWN_FACES_DIR):
        """Inisialisasi service dan memuat seluruh data wajah terdaftar ke memori."""
        self.faces_dir = faces_dir
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []
        self.load_known_faces()

    def _load_face_encoding(self, image_path: str) -> Optional[np.ndarray]:
        """Mengekstraksi vektor encoding wajah pertama yang ditemukan pada sebuah file gambar.

        Args:
            image_path (str): Path absolut atau relatif ke file gambar.

        Returns:
            Optional[np.ndarray]: Vektor encoding wajah 128 dimensi, atau None jika tidak ditemukan wajah.
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        return encodings[0] if encodings else None

    def load_known_faces(self) -> None:
        """Memuat dan mengindeks seluruh file wajah yang ada pada direktori penyimpanan ke dalam RAM.

        Membaca file dengan ekstensi yang diizinkan (jpg, png, webp, dll),
        menghasilkan face encoding, dan menyimpan nama file sebagai identitas orang/siswa.
        """
        os.makedirs(self.faces_dir, exist_ok=True)
        self.known_face_encodings.clear()
        self.known_face_names.clear()

        for filename in sorted(os.listdir(self.faces_dir)):
            if not filename.lower().endswith(FACE_ALLOWED_EXT):
                continue
            try:
                encoding = self._load_face_encoding(os.path.join(self.faces_dir, filename))
            except Exception as e:
                logger.warning(f"Gagal memuat wajah {filename}: {e}")
                continue

            if encoding is not None:
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(filename.rsplit(".", 1)[0])  # Nama file = Nama orang

        logger.info(f"{len(self.known_face_names)} wajah terdaftar dimuat dari {self.faces_dir}")

    def recognize_face_sync(self, img_bgr: np.ndarray) -> Optional[str]:
        """Mencocokkan wajah pada gambar input terhadap daftar wajah terdaftar secara synchronous.

        Args:
            img_bgr (np.ndarray): Gambar input dalam format BGR OpenCV.

        Returns:
            Optional[str]: Nama orang yang terdeteksi jika cocok, atau None jika tidak ada kecocokan.
        """
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img_rgb)
        face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            if True in matches:
                return self.known_face_names[matches.index(True)]
        return None

    async def verify_face(self, face_base64: str) -> Optional[str]:
        """Mendekode gambar base64 dan memverifikasi wajah secara asynchronous tanpa memblokir event loop.

        Args:
            face_base64 (str): Data gambar wajah dalam format Base64.

        Returns:
            Optional[str]: Nama orang yang cocok, atau None jika tidak terdeteksi/tidak dikenal.
        """
        img = decode_base64_image(face_base64)
        return await asyncio.to_thread(self.recognize_face_sync, img)

    def register_face_sync(self, name: str, img_bgr: np.ndarray) -> Tuple[bool, Optional[str], Optional[str]]:
        """Menyimpan file gambar ke disk dan mendaftarkan face encoding ke dalam memori secara synchronous.

        Args:
            name (str): Nama siswa/orang yang didaftarkan.
            img_bgr (np.ndarray): Gambar wajah dalam format BGR OpenCV.

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
                - bool: True jika sukses, False jika gagal.
                - Optional[str]: Nama file yang disimpan (cth: 'nama.jpg').
                - Optional[str]: Pesan kesalahan jika proses registrasi gagal.
        """
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if not encodings:
            return False, None, "Wajah tidak terdeteksi pada gambar!"

        encoding = encodings[0]
        filename = f"{name}.jpg"
        file_path = os.path.join(self.faces_dir, filename)
        cv2.imwrite(file_path, img_bgr)

        # Update cache memori; timpa entri lama jika nama sudah ada
        if name in self.known_face_names:
            self.known_face_encodings[self.known_face_names.index(name)] = encoding
        else:
            self.known_face_names.append(name)
            self.known_face_encodings.append(encoding)

        logger.info(f"Registered face '{name}' ({len(self.known_face_names)} total)")
        return True, filename, None

    async def capture_face(self, name: str, face_base64: str) -> Tuple[str, str]:
        """Validasi nama, decode base64, simpan file, dan perbarui indeks wajah secara asynchronous.

        Args:
            name (str): Nama siswa/orang yang akan didaftarkan.
            face_base64 (str): Data gambar wajah dalam format Base64.

        Returns:
            Tuple[str, str]: Nama yang didaftarkan dan nama file yang tersimpan.

        Raises:
            HTTPException: Status 400 jika nama tidak valid atau wajah tidak terdeteksi pada gambar.
        """
        cleaned_name = name.strip()
        if not cleaned_name or not re.fullmatch(r"[\w\- ]+", cleaned_name):
            raise HTTPException(
                status_code=400,
                detail="Nama tidak valid. Hanya boleh huruf, angka, spasi, - dan _.",
            )

        img = decode_base64_image(face_base64)
        success, filename, err_msg = await asyncio.to_thread(self.register_face_sync, cleaned_name, img)

        if not success:
            raise HTTPException(status_code=400, detail=err_msg)

        return cleaned_name, filename


# Singleton instance untuk digunakan di seluruh modul router
face_service = FaceRecognitionService()
