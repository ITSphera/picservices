# Stage 1: Builder
FROM --platform=linux/amd64 python:3.12.1-slim AS builder

WORKDIR /app

# Install build deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM --platform=linux/amd64 python:3.12.1-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy application files
# COPY .docker/entrypoint.sh .
# RUN chmod +x entrypoint.sh

COPY . .

# ENV PYTHONPATH=/app
# WORKDIR /app
# ENTRYPOINT ["python", "-m", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config log/logconfig.ini"]
ENTRYPOINT ["python", "-c", "import sys; sys.path.append('.'); from uvicorn import run; run('src.main:app', host='0.0.0.0', port=8000)"]
