#!/usr/bin/env python3
"""
ARSA Technology - Edge TTS & Face Recognition Service
Comprehensive User Acceptance Testing (UAT) Suite
"""

import os
import sys
import time
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load env variables
load_dotenv()

API_KEY = os.getenv("API_KEY", "PzunAKM5UtMnM1r2wVMyR_XZJkI1rB9yPupfBVDtMic")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8021")

AUTH_HEADERS = {
    API_KEY_HEADER: API_KEY,
    "Content-Type": "application/json"
}

NO_AUTH_HEADERS = {
    "Content-Type": "application/json"
}

INVALID_AUTH_HEADERS = {
    API_KEY_HEADER: "invalid-key-xyz123",
    "Content-Type": "application/json"
}

results = []

def record_test(test_id, category, name, passed, status_code, details, duration_ms):
    status_icon = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{status_icon}] {test_id} - {name} ({duration_ms:.1f}ms)")
    if not passed:
        print(f"       Details: {details}")
    results.append({
        "id": test_id,
        "category": category,
        "name": name,
        "passed": passed,
        "status_code": status_code,
        "details": details,
        "duration_ms": duration_ms
    })

def image_to_base64(filepath):
    with open(filepath, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

def run_all_tests():
    print("=" * 70)
    print("🚀 ARSA Technology Edge-TTS & Face Recognition - UAT TEST SUITE")
    print(f"📡 Target Server: {BASE_URL}")
    print(f"🔑 Auth Header: {API_KEY_HEADER} (Key: {API_KEY[:6]}...{API_KEY[-4:]})")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. PUBLIC ENDPOINTS (TC-PUB)
    # -------------------------------------------------------------
    print("\n📦 CATEGORY 1: PUBLIC ENDPOINTS")
    
    # TC-PUB-01: Root Endpoint
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/", headers=NO_AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("status") == "running")
        record_test("TC-PUB-01", "Public Endpoints", "Root info endpoint (GET /)", passed, r.status_code, str(data), dur)
    except Exception as e:
        record_test("TC-PUB-01", "Public Endpoints", "Root info endpoint (GET /)", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-PUB-02: Health Check
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/health", headers=NO_AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("status") == "healthy" and data.get("auth_enabled") is True)
        record_test("TC-PUB-02", "Public Endpoints", "Health check with auth status (GET /health)", passed, r.status_code, str(data), dur)
    except Exception as e:
        record_test("TC-PUB-02", "Public Endpoints", "Health check (GET /health)", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-PUB-03: Voice Listing
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/voices", headers=NO_AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else []
        passed = (r.status_code == 200 and isinstance(data, list) and len(data) >= 4)
        voice_names = [v.get("voice_id") for v in data]
        record_test("TC-PUB-03", "Public Endpoints", "Voice listing (GET /voices)", passed, r.status_code, f"{len(data)} voices: {voice_names}", dur)
    except Exception as e:
        record_test("TC-PUB-03", "Public Endpoints", "Voice listing (GET /voices)", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-PUB-04: OpenAPI Documentation
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/openapi.json", headers=NO_AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and "paths" in data)
        record_test("TC-PUB-04", "Public Endpoints", "OpenAPI schema (GET /openapi.json)", passed, r.status_code, f"{len(data.get('paths', {}))} endpoints documented", dur)
    except Exception as e:
        record_test("TC-PUB-04", "Public Endpoints", "OpenAPI schema (GET /openapi.json)", False, 0, str(e), (time.time() - t0) * 1000)

    # -------------------------------------------------------------
    # 2. SECURITY & AUTHENTICATION (TC-SEC)
    # -------------------------------------------------------------
    print("\n🔒 CATEGORY 2: SECURITY & AUTHENTICATION")

    # TC-SEC-01: Missing API Key -> 401
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/tts", headers=NO_AUTH_HEADERS, json={"text": "Tes auth"}, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 401)
        record_test("TC-SEC-01", "Security & Auth", "Protected route without API Key returns 401 Unauthorized", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-SEC-01", "Security & Auth", "Protected route without API Key", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-SEC-02: Invalid API Key -> 403
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/tts", headers=INVALID_AUTH_HEADERS, json={"text": "Tes auth"}, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 403)
        record_test("TC-SEC-02", "Security & Auth", "Protected route with invalid API Key returns 403 Forbidden", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-SEC-02", "Security & Auth", "Protected route with invalid API Key", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-SEC-03: Valid API Key -> 200
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json={"text": "Uji otentikasi kunci API valid.", "voice": "female"}, timeout=20)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 200 and r.json().get("success") is True)
        record_test("TC-SEC-03", "Security & Auth", "Protected route with valid API Key returns 200 OK", passed, r.status_code, f"Audio ID: {r.json().get('audio_id')}", dur)
    except Exception as e:
        record_test("TC-SEC-03", "Security & Auth", "Protected route with valid API Key", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-SEC-04: Rate Limiting Headers
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/stats", headers=AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        has_limit = "x-ratelimit-limit" in r.headers or "X-RateLimit-Limit" in r.headers
        has_remain = "x-ratelimit-remaining" in r.headers or "X-RateLimit-Remaining" in r.headers
        passed = (r.status_code == 200 and has_limit and has_remain)
        headers_info = {k: v for k, v in r.headers.items() if "ratelimit" in k.lower()}
        record_test("TC-SEC-04", "Security & Auth", "Rate limit headers presence", passed, r.status_code, str(headers_info), dur)
    except Exception as e:
        record_test("TC-SEC-04", "Security & Auth", "Rate limit headers presence", False, 0, str(e), (time.time() - t0) * 1000)

    # -------------------------------------------------------------
    # 3. TEXT-TO-SPEECH (TTS) SYNTHESIS (TC-TTS)
    # -------------------------------------------------------------
    print("\n🎤 CATEGORY 3: TEXT-TO-SPEECH (TTS) ENGINES")

    generated_audio_ids = []

    # TC-TTS-01: Indonesian Female Voice (WAV)
    t0 = time.time()
    try:
        payload = {
            "text": "Selamat datang di ARSA Technology. Kami menghadirkan solusi kecerdasan buatan terdepan.",
            "voice": "female",
            "language": "indonesian",
            "output_format": "wav"
        }
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json=payload, timeout=25)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("success") is True and data.get("file_size", 0) > 1000)
        if passed:
            generated_audio_ids.append(data["audio_id"])
        record_test("TC-TTS-01", "TTS Engine", "Indonesian Female Voice - WAV format", passed, r.status_code, f"Voice: {data.get('voice_used')}, Size: {data.get('file_size')}B", dur)
    except Exception as e:
        record_test("TC-TTS-01", "TTS Engine", "Indonesian Female Voice - WAV format", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-TTS-02: Indonesian Male Voice (MP3)
    t0 = time.time()
    try:
        payload = {
            "text": "Sistem verifikasi wajah dan audio bekerja dengan optimal dan presisi tinggi.",
            "voice": "male",
            "language": "indonesian",
            "output_format": "mp3"
        }
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json=payload, timeout=25)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("success") is True and data.get("file_size", 0) > 1000)
        if passed:
            generated_audio_ids.append(data["audio_id"])
        record_test("TC-TTS-02", "TTS Engine", "Indonesian Male Voice - MP3 format", passed, r.status_code, f"Voice: {data.get('voice_used')}, Size: {data.get('file_size')}B", dur)
    except Exception as e:
        record_test("TC-TTS-02", "TTS Engine", "Indonesian Male Voice - MP3 format", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-TTS-03: English Voice with Custom Pitch & Rate
    t0 = time.time()
    try:
        payload = {
            "text": "ARSA Technology delivers high accuracy neural speech synthesis.",
            "voice": "female_us",
            "language": "english",
            "rate": "+15%",
            "pitch": "+20Hz",
            "volume": "+10%",
            "output_format": "wav"
        }
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json=payload, timeout=25)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("success") is True and data.get("file_size", 0) > 1000)
        if passed:
            generated_audio_ids.append(data["audio_id"])
        record_test("TC-TTS-03", "TTS Engine", "English Voice with Custom Pitch & Rate", passed, r.status_code, f"Voice: {data.get('voice_used')}, Size: {data.get('file_size')}B", dur)
    except Exception as e:
        record_test("TC-TTS-03", "TTS Engine", "English Voice with Custom Pitch & Rate", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-TTS-04: Piper Offline Neural Engine
    t0 = time.time()
    try:
        payload = {
            "text": "Testing local offline neural voice synthesis using Piper TTS model.",
            "voice": "en_female",
            "engine": "piper"
        }
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json=payload, timeout=25)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("success") is True and data.get("file_size", 0) > 1000)
        if passed:
            generated_audio_ids.append(data["audio_id"])
        record_test("TC-TTS-04", "TTS Engine", "Piper Offline Neural Engine (Local WAV)", passed, r.status_code, f"Voice: {data.get('voice_used')}, Size: {data.get('file_size')}B", dur)
    except Exception as e:
        record_test("TC-TTS-04", "TTS Engine", "Piper Offline Neural Engine", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-TTS-05: Batch TTS Processing
    t0 = time.time()
    try:
        payload = [
            {"text": "Pesan pertama batch pengujian.", "voice": "female", "language": "indonesian"},
            {"text": "Pesan kedua dengan suara pria.", "voice": "male", "language": "indonesian"},
            {"text": "Third message in English for multilingual test.", "voice": "female_us", "language": "english"}
        ]
        r = requests.post(f"{BASE_URL}/tts/batch", headers=AUTH_HEADERS, json=payload, timeout=40)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("batch_success") is True and data.get("successful") == 3)
        for item in data.get("results", []):
            if item.get("audio_id"):
                generated_audio_ids.append(item["audio_id"])
        record_test("TC-TTS-05", "TTS Engine", "Batch TTS Processing (3 requests)", passed, r.status_code, f"Successful: {data.get('successful')}/{data.get('total_requests')}", dur)
    except Exception as e:
        record_test("TC-TTS-05", "TTS Engine", "Batch TTS Processing", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-TTS-06: Audio Download Endpoint
    t0 = time.time()
    try:
        if generated_audio_ids:
            target_id = generated_audio_ids[0]
            r = requests.get(f"{BASE_URL}/audio/{target_id}", headers=AUTH_HEADERS, timeout=15)
            dur = (time.time() - t0) * 1000
            passed = (r.status_code == 200 and len(r.content) > 1000 and "audio" in r.headers.get("content-type", ""))
            record_test("TC-TTS-06", "TTS Engine", "Audio Download Endpoint (GET /audio/{id})", passed, r.status_code, f"Downloaded {len(r.content)} bytes, Content-Type: {r.headers.get('content-type')}", dur)
        else:
            record_test("TC-TTS-06", "TTS Engine", "Audio Download Endpoint", False, 0, "No audio ID available", 0)
    except Exception as e:
        record_test("TC-TTS-06", "TTS Engine", "Audio Download Endpoint", False, 0, str(e), (time.time() - t0) * 1000)

    # -------------------------------------------------------------
    # 4. FACE RECOGNITION & BIOMETRICS (TC-FACE)
    # -------------------------------------------------------------
    print("\n🧑‍🤝‍🧑 CATEGORY 4: FACE RECOGNITION & BIOMETRICS")

    face1_b64 = image_to_base64("test_face1.jpg") if os.path.exists("test_face1.jpg") else ""
    face2_b64 = image_to_base64("test_face2.jpg") if os.path.exists("test_face2.jpg") else ""

    # TC-FACE-01: Register Face via /capture-face
    t0 = time.time()
    try:
        payload = {
            "name": "Budi_Santoso",
            "face_encoding": face1_b64
        }
        r = requests.post(f"{BASE_URL}/capture-face", headers=AUTH_HEADERS, json=payload, timeout=20)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("status") == "success" and data.get("name") == "Budi_Santoso")
        record_test("TC-FACE-01", "Face Recognition", "Register face image (/capture-face)", passed, r.status_code, str(data), dur)
    except Exception as e:
        record_test("TC-FACE-01", "Face Recognition", "Register face image", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-FACE-02: Verify Registered Face -> Match
    t0 = time.time()
    try:
        payload = {
            "face_encoding": face1_b64
        }
        r = requests.post(f"{BASE_URL}/verify-face", headers=AUTH_HEADERS, json=payload, timeout=20)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (r.status_code == 200 and data.get("status") == "success" and data.get("name") == "Budi_Santoso")
        record_test("TC-FACE-02", "Face Recognition", "Verify registered face correctly identifies person", passed, r.status_code, str(data), dur)
    except Exception as e:
        record_test("TC-FACE-02", "Face Recognition", "Verify registered face", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-FACE-03: Verify Unregistered Face -> Returns 400
    t0 = time.time()
    try:
        payload = {
            "face_encoding": face2_b64
        }
        r = requests.post(f"{BASE_URL}/verify-face", headers=AUTH_HEADERS, json=payload, timeout=20)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code in (200, 400) else {}
        passed = (r.status_code == 400 and data.get("status") == "error")
        record_test("TC-FACE-03", "Face Recognition", "Verify unregistered face returns 400 Not Recognized", passed, r.status_code, str(data), dur)
    except Exception as e:
        record_test("TC-FACE-03", "Face Recognition", "Verify unregistered face", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-FACE-04: Register Face with Invalid Base64 -> 400
    t0 = time.time()
    try:
        payload = {
            "name": "Invalid_User",
            "face_encoding": "not-a-valid-base64-string"
        }
        r = requests.post(f"{BASE_URL}/capture-face", headers=AUTH_HEADERS, json=payload, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 400)
        record_test("TC-FACE-04", "Face Recognition", "Capture face with corrupt base64 returns 400", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-FACE-04", "Face Recognition", "Capture face with corrupt base64", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-FACE-05: Register Face with Invalid Name -> 400
    t0 = time.time()
    try:
        payload = {
            "name": "user!@#$%^&*()",
            "face_encoding": face1_b64
        }
        r = requests.post(f"{BASE_URL}/capture-face", headers=AUTH_HEADERS, json=payload, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 400)
        record_test("TC-FACE-05", "Face Recognition", "Capture face with illegal characters in name returns 400", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-FACE-05", "Face Recognition", "Capture face with illegal name", False, 0, str(e), (time.time() - t0) * 1000)

    # -------------------------------------------------------------
    # 5. INPUT VALIDATION & BOUNDARY TESTS (TC-VAL)
    # -------------------------------------------------------------
    print("\n🛡️ CATEGORY 5: INPUT VALIDATION & BOUNDARY TESTS")

    # TC-VAL-01: Empty Text -> 400
    t0 = time.time()
    try:
        payload = {"text": "   ", "voice": "female"}
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json=payload, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 400)
        record_test("TC-VAL-01", "Input Validation", "TTS request with empty text returns 400", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-VAL-01", "Input Validation", "TTS request with empty text", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-VAL-02: Text Exceeding 5000 chars -> 400
    t0 = time.time()
    try:
        payload = {"text": "A" * 5050, "voice": "female"}
        r = requests.post(f"{BASE_URL}/tts", headers=AUTH_HEADERS, json=payload, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 400)
        record_test("TC-VAL-02", "Input Validation", "TTS request exceeding max length (>5000 chars) returns 400", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-VAL-02", "Input Validation", "TTS request exceeding max length", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-VAL-03: Batch TTS > 10 items -> 400
    t0 = time.time()
    try:
        payload = [{"text": f"Item {i}", "voice": "female"} for i in range(12)]
        r = requests.post(f"{BASE_URL}/tts/batch", headers=AUTH_HEADERS, json=payload, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 400)
        record_test("TC-VAL-03", "Input Validation", "Batch TTS exceeding 10 items returns 400", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-VAL-03", "Input Validation", "Batch TTS exceeding 10 items", False, 0, str(e), (time.time() - t0) * 1000)

    # TC-VAL-04: Non-existent Audio Download -> 404
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/audio/00000000-0000-0000-0000-000000000000", headers=AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        passed = (r.status_code == 404)
        record_test("TC-VAL-04", "Input Validation", "Non-existent audio download returns 404 Not Found", passed, r.status_code, r.text, dur)
    except Exception as e:
        record_test("TC-VAL-04", "Input Validation", "Non-existent audio download", False, 0, str(e), (time.time() - t0) * 1000)

    # -------------------------------------------------------------
    # 6. SERVICE MONITORING & STATS (TC-MON)
    # -------------------------------------------------------------
    print("\n📊 CATEGORY 6: SERVICE MONITORING & STATS")

    # TC-MON-01: Service Stats
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/stats", headers=AUTH_HEADERS, timeout=10)
        dur = (time.time() - t0) * 1000
        data = r.json() if r.status_code == 200 else {}
        passed = (
            r.status_code == 200 and 
            "total_audio_files" in data and 
            "total_size_mb" in data and
            "available_voices" in data
        )
        record_test("TC-MON-01", "Monitoring & Stats", "Service stats endpoint (GET /stats)", passed, r.status_code, str(data), dur)
    except Exception as e:
        record_test("TC-MON-01", "Monitoring & Stats", "Service stats endpoint", False, 0, str(e), (time.time() - t0) * 1000)

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count
    pass_rate = (passed_count / total) * 100 if total > 0 else 0

    print("\n" + "=" * 70)
    print("📊 UAT EXECUTION SUMMARY")
    print(f"Total Tests Executed : {total}")
    print(f"Passed               : {passed_count}")
    print(f"Failed               : {failed_count}")
    print(f"Success Rate         : {pass_rate:.1f}%")
    print("=" * 70)

    # Save JSON report
    with open("uat_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": BASE_URL,
            "total": total,
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate": pass_rate,
            "results": results
        }, f, indent=2)

    return failed_count == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
