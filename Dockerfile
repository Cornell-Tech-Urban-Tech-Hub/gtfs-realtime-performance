# Use Python 3.10
FROM python:3.10-slim

# Install system dependencies for geopandas
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY runner.py .
COPY process_feeds.sh .

# Make the script executable
RUN chmod +x process_feeds.sh

# Set the entrypoint to bash
ENTRYPOINT ["/bin/bash"]
# Use process_feeds.sh as the default command
CMD ["./process_feeds.sh"]
