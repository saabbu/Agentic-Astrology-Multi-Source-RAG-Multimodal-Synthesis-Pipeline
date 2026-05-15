import requests
import time
import json
import confidential 

API_KEY = confidential.heygen_api_key 

HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def upload_audio_asset(file_path):
    url = "https://api.heygen.com/v1/asset/upload"
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
    url = "https://api.heygen.com/v2/video/generate"
    payload = {
        "video_setting": {"ratio": "16:9"},
        "dimension": {"width": 1920, "height": 1080},
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
    if not video_id:
        return None
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    
    while True:
        response = requests.get(url, headers=HEADERS)
        data = response.json().get('data', {})
        status = data.get('status')
        print(f"HeyGen Status: {status}")
        
        if status == "completed":
            video_url = data.get('video_url')
            return video_url
        elif status in ["failed", "rejected"]:
            print(f"Video generation terminated with state: {status}.")
            return None
        time.sleep(30) 

def generate_avatar_video(audio_file_path):
    print(f"Initializing HeyGen video production for track: {audio_file_path}")
    audio_id = upload_audio_asset(audio_file_path)
    if audio_id:
        vid_id = create_video(audio_id)
        return check_status(vid_id)
    return None

if __name__ == "__main__":
    generate_avatar_video("astrology_final_mix.mp3")