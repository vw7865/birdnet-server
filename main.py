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

from birdnet.audio_based_prediction import predict_species_within_audio_file

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
        # Use a consistent filename with proper extension
        temp_file_path = temp_dir / "recording.wav"
        
        # Save the uploaded file
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Run BirdNET analysis
        print(f"Analyzing {temp_file_path}...")
        print(f"File exists: {temp_file_path.exists()}")
        print(f"File size: {temp_file_path.stat().st_size} bytes")
        print(f"Absolute path: {temp_file_path.absolute()}")
        
        try:
            # Use the correct BirdNET API
            print(f"Starting BirdNET analysis...")
            
            # Convert Path to string for BirdNET compatibility
            audio_file_path = str(temp_file_path.absolute())
            print(f"Using audio file path: {audio_file_path}")
            
            # Verify the file is accessible
            if not os.path.exists(audio_file_path):
                raise Exception(f"Audio file not found at path: {audio_file_path}")
            
            # Check file permissions
            if not os.access(audio_file_path, os.R_OK):
                raise Exception(f"Cannot read audio file at path: {audio_file_path}")
            
            print(f"File verification passed. Proceeding with BirdNET analysis...")
            
            # Call BirdNET with the string file path - this returns a generator
            predictions_generator = predict_species_within_audio_file(
                audio_file=audio_file_path,
                min_confidence=0.1,
                silent=True  # Disable progress bar for server use
            )
            
            print(f"BirdNET analysis started successfully")
            
            # Process the generator results
            results = []
            try:
                for (start_time, end_time), species_prediction in predictions_generator:
                    print(f"Processing time interval: {start_time}-{end_time}s")
                    print(f"Found {len(species_prediction)} species in this interval")
                    
                    # Each species_prediction is an OrderedDict with species names as keys and confidence as values
                    for species, confidence in species_prediction.items():
                        result = {
                            "common_name": species,  # e.g., "Poecile atricapillus_Black-capped Chickadee"
                            "confidence": float(confidence),
                            "start_time": float(start_time),
                            "end_time": float(end_time)
                        }
                        results.append(result)
                        print(f"  - {species}: {confidence:.3f}")
            except Exception as generator_error:
                print(f"Error processing generator results: {generator_error}")
                traceback.print_exc()
                # Return empty results instead of failing completely
                results = []
            
            print(f"Analysis complete. Found {len(results)} results.")
            return results

        except Exception as e:
            print(f"BirdNET analysis failed: {e}")
            print(f"Error type: {type(e)}")
            traceback.print_exc()
            raise e

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