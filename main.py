import os
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import librosa
import numpy as np
import tensorflow as tf
import soundfile as sf

app = FastAPI(title="BirdNET-Analyzer API")

# Enable CORS for your iOS app with more permissive settings for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)

# Model configuration
MODEL_PATH = "model/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
SAMPLE_RATE = 48000
SIG_LENGTH = 3.0  # seconds
SIG_OVERLAP = 0.0  # seconds
SIG_MINLEN = 1.0  # seconds

class BirdNetResult(BaseModel):
    species: str
    confidence: float
    startTime: float
    endTime: float

# Load the BirdNET model
interpreter = None

def load_model():
    global interpreter
    if interpreter is None:
        # Download model if not exists
        if not os.path.exists(MODEL_PATH):
            os.makedirs("model", exist_ok=True)
            # TODO: Add code to download the model from BirdNET's repository
            raise HTTPException(status_code=500, detail="BirdNET model not found. Please download it first.")
        
        interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()

def process_audio(audio_data: np.ndarray, sample_rate: int) -> List[BirdNetResult]:
    # Resample if necessary
    if sample_rate != SAMPLE_RATE:
        audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=SAMPLE_RATE)
    
    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Process audio in chunks
    results = []
    chunk_length = int(SIG_LENGTH * SAMPLE_RATE)
    overlap_length = int(SIG_OVERLAP * SAMPLE_RATE)
    
    for i in range(0, len(audio_data) - chunk_length + 1, chunk_length - overlap_length):
        chunk = audio_data[i:i + chunk_length]
        
        # Prepare input
        input_data = np.expand_dims(chunk, axis=0)
        input_data = input_data.astype(np.float32)
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], input_data)
        
        # Run inference
        interpreter.invoke()
        
        # Get output
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        # Process results
        # Note: You'll need to map the output indices to species names
        # This is a simplified example
        for j, confidence in enumerate(output_data[0]):
            if confidence > 0.5:  # Confidence threshold
                results.append(BirdNetResult(
                    species=f"Species_{j}",  # Replace with actual species mapping
                    confidence=float(confidence),
                    startTime=float(i / SAMPLE_RATE),
                    endTime=float((i + chunk_length) / SAMPLE_RATE)
                ))
    
    return results

@app.post("/analyze", response_model=List[BirdNetResult])
async def analyze_audio(audio: UploadFile):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
            # Save uploaded file
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Load and process audio
            audio_data, sample_rate = librosa.load(temp_file.name, sr=None)
            
            # Load model if not loaded
            load_model()
            
            # Process audio
            results = process_audio(audio_data, sample_rate)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Make sure we're binding to all interfaces
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=True) 