# ─────────────────────────────────────────────
# Stage 1: Build environment with Playwright
# ─────────────────────────────────────────────
FROM cnstark/pytorch:2.3.0-py3.10.15-ubuntu22.04 AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl ffmpeg build-essential python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + Chromium
RUN playwright install --with-deps chromium

# ─────────────────────────────────────────────
# Stage 2: Final runtime image
# ─────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies for Chromium
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    libglib2.0-0 libxshmfence1 libpangocairo-1.0-0 \
    fonts-liberation ffmpeg libsndfile1\
    libespeak1 pulseaudio espeak\
    portaudio19-dev python3-pyaudio alsa-utils\
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy Playwright Chromium binaries
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy project files
COPY . .

# Environment variable for Gemini (runtime only)
ENV GEMINI_API_KEY=""

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
