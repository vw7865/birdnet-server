import shutil
import os
import subprocess
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

import numpy  # workaround for some systems
import traceback

# Try importing BirdNET differently
try:
    from birdnet.audio_based_prediction import predict_species_within_audio_file
    BIRDNET_AVAILABLE = True
    BIRDNET_METHOD = "new"
except ImportError as e1:
    print(f"New BirdNET import failed: {e1}")
    try:
        from birdnet import predict_species_within_audio_file
        BIRDNET_AVAILABLE = True
        BIRDNET_METHOD = "old"
    except ImportError as e2:
        print(f"Old BirdNET import failed: {e2}")
        BIRDNET_AVAILABLE = False

app = FastAPI(title="BirdNET-Lite Server")

@app.post("/analyze")
async def analyze_audio(audio: UploadFile = File(...)):
    print(f"Received audio file: {audio.filename}, size: {audio.size} bytes")
    temp_dir = Path("temp_audio")

    try:
        temp_dir.mkdir(exist_ok=True)

        # Step 1: Save uploaded audio file as input.m4a
        input_path = temp_dir / "input.m4a"
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Step 2: Convert input.m4a to recording.wav using ffmpeg
        wav_path = temp_dir / "recording.wav"
        conversion_command = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-ar", "48000",
            "-ac", "1",
            str(wav_path)
        ]
        print(f"Running ffmpeg: {' '.join(conversion_command)}")
        result = subprocess.run(conversion_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(f"ffmpeg conversion failed: {result.stderr.decode()}")

        # Step 3: Verify the converted file
        print(f"Analyzing {wav_path}...")
        print(f"File exists: {wav_path.exists()}")
        print(f"File size: {wav_path.stat().st_size} bytes")
        print(f"Absolute path: {wav_path.resolve()}")

        if not wav_path.is_file():
            raise Exception(f"Converted file not found at {wav_path}")

        # Step 4: Run BirdNET prediction
        print(f"Using BirdNET method: {BIRDNET_METHOD}")
        predictions_generator = predict_species_within_audio_file(wav_path)

        results = []
        for (start_time, end_time), species_prediction in predictions_generator:
            print(f"Interval: {start_time}-{end_time}s, {len(species_prediction)} species")
            for species, confidence in species_prediction.items():
                results.append({
                    "common_name": species,
                    "confidence": float(confidence),
                    "start_time": float(start_time),
                    "end_time": float(end_time)
                })
                print(f"  - {species}: {confidence:.3f}")

        print(f"Analysis complete. Found {len(results)} results.")
        return results

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "An error occurred during analysis.", "details": str(e)})

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

@app.get("/")
def read_root():
    return {"message": "BirdNET-Lite server is running."}

@app.get("/test")
def test_birdnet():
    try:
        if not BIRDNET_AVAILABLE:
            return {"status": "error", "message": "BirdNET library not available"}
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
