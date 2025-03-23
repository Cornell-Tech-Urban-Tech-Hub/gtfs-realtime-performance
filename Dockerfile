# Use Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for geopandas
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/
COPY runner.py .

# Create directories for logs and data
RUN mkdir -p logs
RUN mkdir -p data/raw-speeds

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the script
ENTRYPOINT ["python", "runner.py"]
