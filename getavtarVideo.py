import requests
import time
import json
import confidential  # Added import

# Retrieve key from confidential.py
API_KEY = confidential.heygen_api_key 

HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def upload_audio_asset(file_path):
    """Uploads the local MP3 file to HeyGen's servers."""
    url = "https://api.heygen.com/v1/asset/upload"
    
    # Ensure headers here also use the imported API_KEY
    headers = {"X-Api-Key": API_KEY}
    
    with open(file_path, 'rb') as audio_file:
        files = {'file': audio_file}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return None
        
    asset_id = response.json()['data']['id']
    print(f"Audio uploaded successfully. Asset ID: {asset_id}")
    return asset_id

def create_video(audio_asset_id, avatar_id="josh_lite_20220901"):
    """Triggers the video generation using the uploaded audio."""
    url = "https://api.heygen.com/v2/video/generate"
    
    payload = {
        "video_setting": {
            "ratio": "16:9"
        },
        "dimension": {
            "width": 1920,
            "height": 1080
        },
        "character": {
            "type": "avatar",
            "avatar_id": avatar_id,
            "avatar_style": "normal"
        },
        "input_text": "", 
        "audio_asset_id": audio_asset_id
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"Video creation failed: {response.text}")
        return None
        
    video_id = response.json()['data']['video_id']
    print(f"Video generation started. Video ID: {video_id}")
    return video_id

def check_status(video_id):
    """Polls the API until the video is completed."""
    if not video_id:
        return None
        
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    
    while True:
        response = requests.get(url, headers=HEADERS)
        data = response.json().get('data', {})
        status = data.get('status')
        
        print(f"Current Status: {status}")
        
        if status == "completed":
            video_url = data.get('video_url')
            print(f"Success! Video URL: {video_url}")
            return video_url
        elif status in ["failed", "rejected"]:
            print(f"Video generation {status}.")
            return None
            
        time.sleep(30) 

# --- Execution ---
# Using the output from your getAudioCloud.py script
audio_id = upload_audio_asset("guru_peyarchi_2026_full.mp3")

if audio_id:
    vid_id = create_video(audio_id)
    final_url = check_status(vid_id)