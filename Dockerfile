FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Upgrade pip and install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/database/images \
    /app/results/watermarked_images \
    /app/results/recovered_images \
    /app/results/recovered_watermark \
    /app/blockchain/database \
    /app/configs/database

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create volume mount points
VOLUME ["/app/database/images", "/app/results", "/app/blockchain/database"]

# Default command
CMD ["python", "-m", "pytest", "tests/"]