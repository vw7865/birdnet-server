import shutil
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# This is a workaround for a potential issue on some systems
# with the underlying libraries used by BirdNET.
import numpy

from birdnet import SpeciesPredictions, predict_species_within_audio_file

# Initialize FastAPI app
app = FastAPI(title="BirdNET-Lite Server")

@app.post("/analyze")
async def analyze_audio(audio: UploadFile = File(...)):
    """
    Analyzes an audio file to identify bird species using BirdNET.
    """
    print(f"Received audio file: {audio.filename}, size: {audio.size} bytes")
    temp_dir = Path("temp_audio")
    try:
        # Create a temporary directory to store the uploaded file
        temp_dir.mkdir(exist_ok=True)
        # Use a consistent filename as some libraries might have issues with special characters
        temp_file_path = temp_dir / "recording.tmp"
        
        # Save the uploaded file
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Run BirdNET analysis
        print(f"Analyzing {temp_file_path}...")
        print(f"File exists: {temp_file_path.exists()}")
        print(f"File size: {temp_file_path.stat().st_size} bytes")
        
        try:
            # Try with Path object first
            predictions = SpeciesPredictions(predict_species_within_audio_file(temp_file_path))
        except Exception as birdnet_error:
            print(f"BirdNET analysis error with Path: {birdnet_error}")
            try:
                # Try with string path
                predictions = SpeciesPredictions(predict_species_within_audio_file(str(temp_file_path)))
            except Exception as birdnet_error2:
                print(f"BirdNET analysis error with string: {birdnet_error2}")
                # Try with absolute path
                predictions = SpeciesPredictions(predict_species_within_audio_file(str(temp_file_path.absolute())))

        # Format results to match the iOS app's expectation
        results = []
        # The 'predictions' object contains items where the key is a time tuple (start, end)
        # and the value is another object containing species predictions for that time slice.
        for (start_time, end_time), species_prediction in predictions.items():
            # A time slice might have multiple species predictions.
            for species, confidence in species_prediction.items():
                result = {
                    "common_name": species, # e.g., "Poecile atricapillus_Black-capped Chickadee"
                    "confidence": confidence,
                    "start_time": start_time,
                    "end_time": end_time
                }
                results.append(result)
        
        print(f"Analysis complete. Found {len(results)} results.")
        return results

    except Exception as e:
        print(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"error": "An error occurred during analysis.", "details": str(e)})
    finally:
        # Clean up the temporary file and directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

@app.get("/")
def read_root():
    return {"message": "BirdNET-Lite server is running."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 