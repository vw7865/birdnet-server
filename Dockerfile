FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Download the BirdNET model (optional: you can also do this manually)
RUN python download_model.py

# Expose port

EXPOSE 8080

# Start the server
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8080"] 