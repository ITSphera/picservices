# Use multi-stage build to keep the final image clean and small
# First stage: build
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create directories
RUN mkdir -p /app/requirements && mkdir -p /app/log/gunicorn

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y postgresql-client libpq-dev gettext gcc && \
    pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements from high level
COPY /requirements /app/requirements

# Install Python dependencies
ARG ENVIRONMENT
RUN pip install --user -r requirements/requirements.txt

# Second stage: runtime
FROM python:3.12-slim

# Copy virtual environment from builder
COPY --from=builder /root/.local /root/.local

# Ensure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

COPY .docker/entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

