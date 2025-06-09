# BirdNET-Analyzer Server

This is a FastAPI-based server that provides an API endpoint for bird sound analysis using BirdNET.

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the BirdNET model:
```bash
python download_model.py
```

## Running the Server

Start the server with:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## API Endpoints

### POST /analyze
Upload an audio file for bird sound analysis.

**Request:**
- Content-Type: multipart/form-data
- Body: audio file (m4a format)

**Response:**
```json
[
  {
    "species": "string",
    "confidence": 0.0,
    "startTime": 0.0,
    "endTime": 0.0
  }
]
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Development

- The server uses FastAPI for the API framework
- BirdNET model is loaded using TensorFlow Lite
- Audio processing is done using librosa
- CORS is enabled for development (should be restricted in production)

## Production Deployment

For production deployment:
1. Update CORS settings in `main.py` to only allow your app's domain
2. Use a proper WSGI server like Gunicorn
3. Set up proper SSL/TLS
4. Consider using a reverse proxy like Nginx
5. Implement proper error handling and logging
6. Add authentication if needed

## Notes

- The server requires about 1GB of RAM to run the model
- Processing time depends on the length of the audio file
- The model supports 6,000+ bird species
- Audio files should be in m4a format 