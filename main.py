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
            print(f"Starting BirdNET analysis...")
            
            # Use Path object directly, don't convert to string
            audio_file_path = temp_file_path.resolve()
            print(f"Using audio file path (Path object): {audio_file_path}")
    
            # Verify the file is accessible using Path object
            if not audio_file_path.is_file():
                raise Exception(f"Audio file not found at path: {audio_file_path}")
            
            print(f"File verification passed. Proceeding with BirdNET analysis...")
            print(f"Using BirdNET method: {BIRDNET_METHOD}")
            
            # Call BirdNET with the Path object converted to string only for the function call
            predictions_generator = predict_species_within_audio_file(audio_file_path)
            print(f"BirdNET function call successful")
        
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
                print(f"Analysis complete. Found {len(results)} results.")
                return results
            except Exception as generator_error:
                print(f"Error processing generator results: {generator_error}")
                traceback.print_exc()
                # Return empty results instead of failing completely
                return []

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