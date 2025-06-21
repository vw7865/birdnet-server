import shutil
import os
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# This is a workaround for a potential issue on some systems
# with the underlying libraries used by BirdNET.
import numpy
import traceback

# Try importing BirdNET differently
try:
    # Try the newer import first
    from birdnet.audio_based_prediction import predict_species_within_audio_file
    BIRDNET_AVAILABLE = True
    BIRDNET_METHOD = "new"
except ImportError as e1:
    print(f"New BirdNET import failed: {e1}")
    try:
        # Try the older import
        from birdnet import predict_species_within_audio_file
        BIRDNET_AVAILABLE = True
        BIRDNET_METHOD = "old"
    except ImportError as e2:
        print(f"Old BirdNET import failed: {e2}")
        BIRDNET_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(title="BirdNET-Lite Server")

@app.post("/analyze")
async def analyze_audio(audio: UploadFile = File(...)):
    """
    Analyzes an audio file to identify bird species using BirdNET.
    """
    print(f"Received audio file: {audio.filename}, size: {audio.size} bytes")
    
    # For now, return mock results while we debug BirdNET
    print("Returning mock results for testing...")
    
    # Mock bird detection results
    mock_results = [
        {
            "common_name": "Poecile atricapillus_Black-capped Chickadee",
            "confidence": 0.85,
            "start_time": 0.0,
            "end_time": 3.0
        },
        {
            "common_name": "Cardinalis cardinalis_Northern Cardinal", 
            "confidence": 0.72,
            "start_time": 0.0,
            "end_time": 3.0
        },
        {
            "common_name": "Turdus migratorius_American Robin",
            "confidence": 0.68,
            "start_time": 0.0,
            "end_time": 3.0
        }
    ]
    
    print(f"Returning {len(mock_results)} mock results")
    return mock_results

@app.get("/")
def read_root():
    return {"message": "BirdNET-Lite server is running."}

@app.get("/test")
def test_birdnet():
    """
    Test endpoint to verify BirdNET library functionality
    """
    try:
        if not BIRDNET_AVAILABLE:
            return {"status": "error", "message": "BirdNET library not available"}
        
        # Test if we can import and access BirdNET functions
        import birdnet
        return {
            "status": "success", 
            "message": "BirdNET library is available",
            "method": BIRDNET_METHOD,
            "birdnet_version": getattr(birdnet, '__version__', 'unknown')
        }
    except Exception as e:
        return {"status": "error", "message": f"BirdNET test failed: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 