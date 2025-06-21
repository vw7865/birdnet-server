import shutil
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# This is a workaround for a potential issue on some systems
# with the underlying libraries used by BirdNET.
import numpy
import traceback

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
            # Use the correct BirdNET API - pass the file path as string
            file_path_str = str(temp_file_path.absolute())
            print(f"Using file path: {file_path_str}")
            
            # Call the BirdNET function directly
            predictions = predict_species_within_audio_file(file_path_str)
            print(f"Raw predictions: {predictions}")
            
            # Convert to SpeciesPredictions object
            species_predictions = SpeciesPredictions(predictions)
            print(f"Species predictions created successfully")
            
        except Exception as e:
            print(f"BirdNET analysis failed: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise e

        # Format results to match the iOS app's expectation
        results = []
        # The 'predictions' object contains items where the key is a time tuple (start, end)
        # and the value is another object containing species predictions for that time slice.
        for (start_time, end_time), species_prediction in species_predictions.items():
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