"""Modul skema data (Pydantic models) untuk validasi request dan response API."""

from typing import Optional
from pydantic import BaseModel, Field
from src.config import DEFAULT_ENGINE


class TTSRequest(BaseModel):
    """Skema data untuk permintaan sintesis Text-to-Speech tunggal.

    Attributes:
        text (str): Teks yang akan diubah menjadi suara.
        voice (str): ID suara yang digunakan (cth: 'female', 'male', 'en_female').
        rate (str): Kecepatan pengucapan (cth: '+10%', '-10%').
        pitch (str): Nada frekuensi suara (cth: '+25Hz', '-10Hz').
        volume (str): Tingkat volume suara (cth: '+0%', '-20%').
        language (str): Bahasa teks, misalnya 'indonesian' atau 'english'.
        output_format (str): Format file output yang diinginkan ('wav' atau 'mp3').
        engine (str): Mesin TTS yang digunakan ('edge' untuk online atau 'piper' untuk offline neural).
    """

    text: str = Field(..., description="Teks yang akan dikonversi menjadi audio ucapan")
    voice: str = Field(default="female", description="Identifier karakter suara yang dipilih")
    rate: str = Field(default="+0%", description="Modifikasi kecepatan bicara (-50% s/d +100%)")
    pitch: str = Field(default="+0Hz", description="Modifikasi tinggi-rendah nada (-50Hz s/d +50Hz)")
    volume: str = Field(default="+0%", description="Modifikasi volume audio (-50% s/d +50%)")
    language: str = Field(default="indonesian", description="Bahasa teks ('indonesian' atau 'english')")
    output_format: str = Field(default="wav", description="Format container audio ('wav' atau 'mp3')")
    engine: str = Field(default=DEFAULT_ENGINE, description="Engine TTS yang dipilih ('edge' atau 'piper')")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Selamat datang di ARSA Technology, perusahaan AI terdepan di Indonesia",
                "voice": "female",
                "rate": "+10%",
                "pitch": "+25Hz",
                "language": "indonesian",
                "output_format": "wav",
                "engine": "edge",
            }
        }


class TTSResponse(BaseModel):
    """Skema data untuk respons hasil pembuatan audio TTS.

    Attributes:
        success (bool): Status keberhasilan proses sintesis.
        message (str): Pesan status atau keterangan.
        audio_id (str): UUID unik yang mewakili file audio hasil generate.
        audio_url (str): Endpoint URL relatif untuk mendownload file audio.
        duration_estimate (Optional[float]): Estimasi durasi audio dalam satuan detik.
        voice_used (str): Nama model suara lengkap yang digunakan.
        file_size (Optional[int]): Ukuran file audio yang dihasilkan dalam satuan byte.
    """

    success: bool = Field(..., description="Menandakan apakah pembuatan audio berhasil")
    message: str = Field(..., description="Pesan deskriptif hasil operasi")
    audio_id: str = Field(..., description="Identifier unik audio yang dapat digunakan untuk unduhan")
    audio_url: str = Field(..., description="URL endpoint untuk mengunduh audio yang dihasilkan")
    duration_estimate: Optional[float] = Field(None, description="Estimasi panjang durasi audio dalam detik")
    voice_used: str = Field(..., description="Nama model voice yang aktif digunakan")
    file_size: Optional[int] = Field(None, description="Ukuran file dalam satuan byte")


class FaceVerifyRequest(BaseModel):
    """Skema data untuk permintaan verifikasi/pengenalan wajah.

    Attributes:
        face_encoding (str): String gambar dalam format Base64 (opsional dengan prefix data URI).
    """

    face_encoding: str = Field(
        ...,
        description="Data gambar berformat Base64 yang berisi wajah untuk diverifikasi terhadap database wajah terdaftar",
    )


class FaceCaptureRequest(BaseModel):
    """Skema data untuk registrasi wajah baru ke dalam sistem.

    Attributes:
        name (str): Nama identitas orang/siswa yang akan dijadikan nama file dan label.
        face_encoding (str): String gambar dalam format Base64 (opsional dengan prefix data URI).
    """

    name: str = Field(
        ...,
        description="Nama orang/siswa yang akan didaftarkan (hanya huruf, angka, spasi, dash, underscore)",
    )
    face_encoding: str = Field(
        ...,
        description="Data gambar berformat Base64 yang berisi wajah yang akan didaftarkan",
    )


class VoiceInfo(BaseModel):
    """Skema data untuk informasi detail karakter suara TTS yang tersedia.

    Attributes:
        voice_id (str): ID unik suara yang digunakan pada request TTS.
        name (str): Nama lengkap/internal model suara.
        gender (str): Gender suara ('Female', 'Male', atau 'Unknown').
        description (str): Penjelasan profil dan karakteristik suara.
        language (str): Bahasa utama suara ('Indonesian' atau 'English').
        engine (str): Engine yang menjalankan suara ('edge' atau 'piper').
    """

    voice_id: str = Field(..., description="Identifier ringkas suara untuk parameter request")
    name: str = Field(..., description="Nama resmi atau model suara")
    gender: str = Field(..., description="Jenis kelamin suara (Female/Male/Unknown)")
    description: str = Field(..., description="Deskripsi karakter vokal dan gaya suara")
    language: str = Field(..., description="Bahasa yang didukung oleh profil suara ini")
    engine: str = Field(default="edge", description="Engine yang memproses suara ini ('edge' atau 'piper')")
