FROM python:3.12-slim

# Set working directory in one step
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update -y && \
    apt-get install -y libpq-dev gcc netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements /app/requirements

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/requirements.txt

# Copy the application code
COPY . /app
COPY .docker/entrypoint.sh /app

# Copy entrypoint.sh and make it executable

RUN chmod +x .docker/entrypoint.sh
#ENTRYPOINT ["ls"]
ENTRYPOINT ["sh", ".docker/entrypoint.sh"]
