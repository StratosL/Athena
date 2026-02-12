# Using faster-whisper (CTranslate2 implementation) - much faster than OpenAI's whisper
FROM python:3.11-slim-bookworm

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create cache directory for model downloads and set permissions
RUN mkdir -p /app/models /app/.cache && \
    chown -R appuser:appuser /app

# Copy application code
COPY watcher.py .

# Create directories with proper permissions
RUN mkdir -p /watch /output && \
    chown -R appuser:appuser /watch /output /app

# Switch to non-root user
USER appuser

# Set cache directory for Hugging Face
ENV HF_HOME=/app/.cache \
    TRANSFORMERS_CACHE=/app/.cache \
    XDG_CACHE_HOME=/app/.cache

# Environment variables
ENV WATCH_DIR=/watch \
    OUTPUT_DIR=/output \
    WHISPER_MODEL=base.en \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; import sys; sys.exit(0 if os.path.exists('$WATCH_DIR') else 1)"

# Run the watcher
CMD ["python", "watcher.py"]