FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (build-essential and cmake needed for dlib/face_recognition, libgl1/libglib for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ffmpeg \
    cmake \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY download_piper_voices.py .

# Create output, piper voices, and known faces directories with proper permissions
RUN mkdir -p /app/output /app/piper_voices /app/faces && \
    chmod 777 /app/output /app/piper_voices /app/faces

# Create non-root user for security
RUN useradd -m -u 1000 ttsuser && \
    chown -R ttsuser:ttsuser /app

# Switch to non-root user
USER ttsuser

# Expose port
EXPOSE 8021

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8021/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8021", "--workers", "1"]