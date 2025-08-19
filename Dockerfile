# Stage 1: Build environment
FROM cnstark/pytorch:2.3.0-py3.10.15-ubuntu22.04 AS builder

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install only Chromium for Playwright (faster than all browsers)
RUN playwright install --with-deps chromium

# Stage 2: Final lightweight image
FROM python:3.12-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set PATH for conda-based pytorch image
ENV PATH="/opt/conda/bin:$PATH"

# Copy project files
COPY . .

# Environment variables for API key
ENV GEMINI_API_KEY=${GEMINI_API_KEY}

# Expose ports
EXPOSE 8501 8000

# Default: Streamlit
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
