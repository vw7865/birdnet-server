import os
import requests

def download_file(url: str, filename: str):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.status_code} {response.reason}")
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'wb') as file:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
    
    # Check file size
    file_size = os.path.getsize(filename)
    print(f"Downloaded file size: {file_size} bytes")
    if file_size < 50_000_000:  # Should be >50MB (actual model size is ~51.7MB)
        raise Exception("Downloaded model file is too small! Download failed or incomplete.")

def main():
    model_url = "https://github.com/woheller69/whoBIRD-TFlite/raw/master/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
    model_path = "model/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite"
    
    print("Downloading BirdNET model...")
    download_file(model_url, model_path)
    print("Download complete!")

if __name__ == "__main__":
    main()