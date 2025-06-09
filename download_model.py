import os
import requests
from tqdm import tqdm

def download_file(url: str, filename: str):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

def main():
    # BirdNET model URL (you'll need to replace this with the actual URL)
    model_url = "https://github.com/kahst/BirdNET-Analyzer/raw/main/model/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
    model_path = "model/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
    
    print("Downloading BirdNET model...")
    download_file(model_url, model_path)
    print("Download complete!")

if __name__ == "__main__":
    main() 