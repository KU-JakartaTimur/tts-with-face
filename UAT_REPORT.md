# 📋 LAPORAN USER ACCEPTANCE TESTING (UAT)

**Nama Project:** ARSA Technology - Edge TTS & Face Recognition Service  
**Repository / Direktori:** `D:\DEV\Python\ttswithface`  
**Tanggal Pengujian:** 28 Agustus 2026  
**Versi Aplikasi:** 1.0.0  
**Target Server:** `http://127.0.0.1:8021`  
**Penguji:** Automated UAT Test Suite (`uat_suite.py`)  
**Hasil Akhir:** ✅ **LULUS SEMUA PENGUJIAN (100.0% PASS - 24/24 Test Cases)**

---

## 📑 Daftar Isi
1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Lingkungan Pengujian](#2-lingkungan-pengujian)
3. [Matriks & Hasil Pengujian per Kategori](#3-matriks--hasil-pengujian-per-kategori)
   - [A. Public Endpoints & Dokumentasi (TC-PUB)](#a-public-endpoints--dokumentasi-tc-pub)
   - [B. Keamanan & Otentikasi (TC-SEC)](#b-keamanan--otentikasi-tc-sec)
   - [C. Text-to-Speech (TTS) Engines (TC-TTS)](#c-text-to-speech-tts-engines-tc-tts)
   - [D. Pengenalan Wajah & Biometrik (TC-FACE)](#d-pengenalan-wajah--biometrik-tc-face)
   - [E. Validasi Input & Boundary (TC-VAL)](#e-validasi-input--boundary-tc-val)
   - [F. Monitoring & Statistik (TC-MON)](#f-monitoring--statistik-tc-mon)
4. [Temuan Bug & Solusi Perbaikan](#4-temuan-bug--solusi-perbaikan)
5. [Cara Menjalankan UAT Mandiri](#5-cara-menjalankan-uat-mandiri)
6. [Kesimpulan & Rekomendasi](#6-kesimpulan--rekomendasi)

---

## 1. Ringkasan Eksekutif

Pengujian penerimaan pengguna (User Acceptance Testing / UAT) dilakukan secara komprehensif untuk memastikan seluruh fitur aplikasi ARSA Technology Edge-TTS & Face Recognition API berfungsi sesuai spesifikasi teknis, memiliki mekanisme keamanan yang handal, serta tahan terhadap input tidak valid.

### 📊 Statistik Hasil Pengujian:
```
======================================================================
Total Test Cases Executed : 24
Passed                    : 24 (100.0%)
Failed                    : 0  (0.0%)
Success Rate              : 100.0%
Status Kesiapan Rilis     : READY FOR PRODUCTION (SIAP PRODUKSI)
======================================================================
```

---

## 2. Lingkungan Pengujian

| Komponen | Spesifikasi / Konfigurasi |
| :--- | :--- |
| **Sistem Operasi** | Windows (64-bit) |
| **Python Runtime** | Python 3.12.10 |
| **Framework Web** | FastAPI 0.115.12 + Uvicorn 0.34.3 |
| **TTS Engines** | Microsoft Edge TTS (Online) + Piper Neural TTS (Offline ONNX) |
| **Computer Vision** | OpenCV 4.10.0 + dlib-bin 20.0.1 + face_recognition 1.3.0 |
| **Otentikasi** | Header `X-API-Key` (Single/Multi-key constant-time comparison) |
| **Rate Limiter** | slowapi 0.1.9 (`memory://` store) |

---

## 3. Matriks & Hasil Pengujian per Kategori

### A. Public Endpoints & Dokumentasi (TC-PUB)
*Tujuan: Memastikan endpoint publik dapat diakses tanpa hambatan dan dokumentasi API tersedia lengkap.*

| ID Test | Skenario Pengujian | Endpoint / Method | Hasil | Durasi | Detail Respon |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **TC-PUB-01** | Informasi Layanan | `GET /` | ✅ **PASS** | 11.0 ms | Mengembalikan status `running`, versi, deskripsi layanan, dan daftar endpoint. |
| **TC-PUB-02** | Health Check & Status Engine | `GET /health` | ✅ **PASS** | 4.2 ms | Status `healthy`, `auth_enabled: true`, status Edge & Piper engine bernilai `True`. |
| **TC-PUB-03** | Katalog Suara TTS | `GET /voices` | ✅ **PASS** | 5.2 ms | Mengembalikan daftar suara Indonesia (`female`, `male`), English (`female_us`, `male_us`), dan Piper lokal (`id_female`, `en_female`, `en_male`). |
| **TC-PUB-04** | Skema OpenAPI & Swagger | `GET /openapi.json` | ✅ **PASS** | 28.0 ms | Skema OpenAPI 3.1.0 tergenerasi lengkap dengan seluruh endpoint dan skema payload. |

---

### B. Keamanan & Otentikasi (TC-SEC)
*Tujuan: Memverifikasi sistem proteksi API key dan rate limiting.*

| ID Test | Skenario Pengujian | Endpoint / Method | Hasil | Durasi | Detail Respon |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **TC-SEC-01** | Akses tanpa `X-API-Key` | `POST /tts` | ✅ **PASS** | 25.3 ms | Menolak request dengan `401 Unauthorized` (*"Missing API key"*). |
| **TC-SEC-02** | Akses dengan API Key salah | `POST /tts` | ✅ **PASS** | 29.6 ms | Menolak request dengan `403 Forbidden` (*"Invalid API key"*). |
| **TC-SEC-03** | Akses dengan API Key valid | `POST /tts` | ✅ **PASS** | 733.6 ms | Menerima request dengan `200 OK` dan menghasilkan file audio. |
| **TC-SEC-04** | Header Rate Limiting | `GET /stats` | ✅ **PASS** | 24.6 ms | Header `X-RateLimit-Limit`, `X-RateLimit-Remaining`, dan `X-RateLimit-Reset` disertakan pada respon. |

---

### C. Text-to-Speech (TTS) Engines (TC-TTS)
*Tujuan: Menguji sintesis suara Bahasa Indonesia, Bahasa Inggris, kustom parameter, Piper offline, dan batch processing.*

| ID Test | Skenario Pengujian | Parameter Payload | Hasil | Durasi | Detail Respon |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **TC-TTS-01** | Bahasa Indonesia Wanita (WAV) | `voice: "female"`, `lang: "indonesian"`, `format: "wav"` | ✅ **PASS** | 691.4 ms | Voice `id-ID-GadisNeural`, file WAV valid berukuran ~49.8 KB. |
| **TC-TTS-02** | Bahasa Indonesia Pria (MP3) | `voice: "male"`, `lang: "indonesian"`, `format: "mp3"` | ✅ **PASS** | 681.1 ms | Voice `id-ID-ArdiNeural`, file MP3 valid berukuran ~30.5 KB. |
| **TC-TTS-03** | English dengan Pitch & Rate Kustom | `rate: "+15%"`, `pitch: "+20Hz"`, `volume: "+10%"` | ✅ **PASS** | 714.9 ms | Voice `en-US-AriaNeural`, parameter terproses sempurna. |
| **TC-TTS-04** | Piper Offline Neural TTS | `engine: "piper"`, `voice: "en_female"` | ✅ **PASS** | 1433.0 ms | Berhasil sintesis offline via model ONNX lokal (`en_US-lessac-medium`). |
| **TC-TTS-05** | Batch TTS Processing | 3 permintaan batch (Indonesian + English) | ✅ **PASS** | 1842.4 ms | `batch_success: true`, 3/3 permintaan berhasil disintesis secara paralel. |
| **TC-TTS-06** | Unduh File Audio | `GET /audio/{audio_id}` | ✅ **PASS** | 30.3 ms | Berhasil stream file audio dengan media-type `audio/wav` / `audio/mpeg`. |

---

### D. Pengenalan Wajah & Biometrik (TC-FACE)
*Tujuan: Menguji registrasi wajah, ekstraksi encoding 128-d, verifikasi kesesuaian wajah, dan deteksi wajah tak dikenal.*

| ID Test | Skenario Pengujian | Input Data | Hasil | Durasi | Detail Respon |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **TC-FACE-01** | Registrasi Wajah Baru | `name: "Budi_Santoso"`, `face_encoding: <base64>` | ✅ **PASS** | 862.2 ms | Berhasil mendeteksi wajah, mengindeks encoding, dan menyimpan gambar ke `./app/faces/Budi_Santoso.jpg`. |
| **TC-FACE-02** | Verifikasi Wajah Cocok | Foto wajah terdaftar (`Budi_Santoso`) | ✅ **PASS** | 874.6 ms | `status: "success"`, berhasil mengidentifikasi nama `Budi_Santoso`. |
| **TC-FACE-03** | Verifikasi Wajah Tak Terdaftar | Foto wajah orang lain | ✅ **PASS** | 532.0 ms | Mengembalikan `400 Bad Request` (*"Wajah tidak terdeteksi atau tidak dikenali!"*). |
| **TC-FACE-04** | Registrasi Base64 Corrupt | String base64 rusak / tidak valid | ✅ **PASS** | 26.5 ms | Ditolak dengan `400 Bad Request` (*"Base64 gambar tidak valid!"*). |
| **TC-FACE-05** | Registrasi Karakter Nama Ilegal | `name: "user!@#$%^&*()"` | ✅ **PASS** | 5.9 ms | Ditolak dengan `400 Bad Request` (*"Nama tidak valid"*). |

---

### E. Validasi Input & Boundary (TC-VAL)
*Tujuan: Memastikan API memvalidasi input ekstrim, batas payload, dan menangani error secara elegan.*

| ID Test | Skenario Pengujian | Kondisi Uji | Hasil | Durasi | Detail Respon |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **TC-VAL-01** | Input Teks Kosong | `text: "   "` | ✅ **PASS** | 26.0 ms | Ditolak dengan `400 Bad Request` (*"Text cannot be empty"*). |
| **TC-VAL-02** | Teks Melebihi Maksimum | `text` sepanjang 5.050 karakter (> 5000) | ✅ **PASS** | 5.3 ms | Ditolak dengan `400 Bad Request` (*"Text too long"*). |
| **TC-VAL-03** | Batch Melebihi Kuota | 12 request dalam 1 batch (> 10) | ✅ **PASS** | 23.2 ms | Ditolak dengan `400 Bad Request` (*"Maximum 10 requests per batch"*). |
| **TC-VAL-04** | Audio ID Tidak Ditemukan | `audio_id: "00000000-0000-0000-0000-000000000000"` | ✅ **PASS** | 29.7 ms | Mengembalikan `404 Not Found` (*"Audio file not found"*). |

---

### F. Monitoring & Statistik (TC-MON)
*Tujuan: Memverifikasi endpoint metrik dan pemantauan sistem.*

| ID Test | Skenario Pengujian | Endpoint | Hasil | Durasi | Detail Respon |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **TC-MON-01** | Statistik Layanan Real-time | `GET /stats` | ✅ **PASS** | 30.7 ms | Mengembalikan total file audio, total ukuran direktori (MB), jumlah suara tersedia, limit karakter, dan interval auto-cleanup. |

---

## 4. Temuan Bug & Solusi Perbaikan

Selama proses pelaksanaan UAT, ditemukan beberapa kendala teknis yang langsung ditangani dan diperbaiki:

### 1. SlowAPI Parameter Injection Exception
- **Gejala:** Request ke endpoint dengan decorator `@limiter.limit` menghasilkan HTTP 500 dengan error: `Exception: parameter 'response' must be an instance of starlette.responses.Response`.
- **Penyebab:** Ketika `headers_enabled=True` diaktifkan pada SlowAPI, fungsi handler FastAPI harus menyertakan parameter `response: Response` agar SlowAPI dapat menginjeksi header `X-RateLimit-*`.
- **Solusi:** Menambahkan parameter `response: Response` pada semua fungsi route terproteksi di [`main.py`](file:///D:/DEV/Python/ttswithface/main.py).

### 2. Integrasi Piper Offline TTS (`synthesize_wav`)
- **Gejala:** Request TTS dengan `engine: "piper"` gagal dengan pesan `# channels not specified`.
- **Penyebab:** `PiperVoice.synthesize()` mengembalikan generator audio chunk, bukan menulis langsung ke objek `wave.open()`.
- **Solusi:** Memperbarui fungsi `synthesize_piper()` di [`main.py`](file:///D:/DEV/Python/ttswithface/main.py) untuk memanggil method `piper_voice.synthesize_wav(text, wav_file)` yang secara otomatis mengonfigurasi header WAV, jumlah channel, dan sample rate.

### 3. Otomatisasi Pembacaan Environment Variable
- **Gejala:** `API_KEY` tidak termuat secara otomatis saat server atau client dijalankan tanpa export environment manual.
- **Solusi:** Menambahkan `from dotenv import load_dotenv; load_dotenv()` di [`main.py`](file:///D:/DEV/Python/ttswithface/main.py) dan [`test_client.py`](file:///D:/DEV/Python/ttswithface/test_client.py).

### 4. Kompatibilitas Encoding Windows Console
- **Gejala:** Crash `UnicodeEncodeError` pada terminal Windows dengan codepage cp1252 saat mencetak simbol/emoji.
- **Solusi:** Menambahkan konfigurasi `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` pada script CLI [`download_piper_voices.py`](file:///D:/DEV/Python/ttswithface/download_piper_voices.py), [`test_client.py`](file:///D:/DEV/Python/ttswithface/test_client.py), dan [`uat_suite.py`](file:///D:/DEV/Python/ttswithface/uat_suite.py).

### 5. Pembaruan Dependencies
- **Gejala:** `face-recognition-models` membutuhkan `pkg_resources` yang telah dipisahkan pada versi setuptools modern.
- **Solusi:** Menambahkan `setuptools<70` dan `python-dotenv>=1.0.0` ke dalam [`requirements.txt`](file:///D:/DEV/Python/ttswithface/requirements.txt).

---

## 5. Cara Menjalankan UAT Mandiri

Untuk menjalankan kembali pengujian UAT secara otomatis di masa mendatang:

```powershell
# 1. Pastikan dependencies terpasang
.\venv\Scripts\pip.exe install -r requirements.txt

# 2. Jalankan server (jika belum berjalan)
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8021

# 3. Jalankan suite UAT lengkap di terminal baru
.\venv\Scripts\python.exe uat_suite.py

# 4. Atau jalankan test client standar
.\venv\Scripts\python.exe test_client.py 127.0.0.1
```

---

## 6. Kesimpulan & Rekomendasi

1. **Status UAT:** **PASSED (100% LULUS)**. Seluruh 24 skenario pengujian fungsional, keamanan, validasi, dan performa telah berhasil dijalankan tanpa kegagalan.
2. **Kesiapan Rilis:** Project **ARSA Technology - Edge TTS & Face Recognition Service** dinyatakan **STABIL & SIAP PRODUKSI (PRODUCTION-READY)**.
3. **Rekomendasi Operasional:**
   - Gunakan HTTPS / reverse proxy (seperti Nginx atau Caddy) untuk penggelaran di lingkungan produksi publik.
   - Bila menggunakan multi-instance/multi-worker di Docker Compose atau Kubernetes, atur `RATE_LIMIT_STORAGE_URI=redis://<redis_host>:6379` agar kuota rate limiter terpusat.
