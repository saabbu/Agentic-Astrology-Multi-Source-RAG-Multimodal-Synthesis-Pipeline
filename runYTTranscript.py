import json
import time
import random
import re
import http.cookiejar
import pandas as pd
import confidential
from datetime import datetime, timedelta
from requests import Session
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# --- Global Client Initialization ---
# This remains global as the API connection configuration is shared across runs
ytclient = build('youtube', 'v3', developerKey=confidential.yt_google_api_key)

# --- Utility Functions ---

def load_cookies_to_session(cookie_file_path):
    """Loads a Netscape formatted cookies.txt file into a requests Session."""
    session = Session()
    cj = http.cookiejar.MozillaCookieJar(cookie_file_path)
    try:
        cj.load(ignore_discard=True, ignore_expires=True)
        session.cookies.update(cj)
        return session
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return None

def get_latest_videos(query, max_results=None, lookback_days=None):
    """Fetches recent video IDs based on dynamic relevance and duration parameters."""
    # Fallback to confidential configurations if parameters aren't explicitly passed
    days = lookback_days if lookback_days is not None else getattr(confidential, 'date_time_lookout', 60)
    limit = max_results if max_results is not None else getattr(confidential, 'max_results', 5)
    primary_lang = confidential.language[0] if getattr(confidential, 'language', None) else 'ta'
    
    timelimit = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
    
    request = ytclient.search().list(
        q=query,
        part='snippet',
        maxResults=limit,
        type='video',
        videoDuration='medium',
        order='relevance',
        publishedAfter=timelimit,
        relevanceLanguage=primary_lang
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response['items']]

# --- Extraction Pipeline ---

def pipeline_to_json_with_cookies(video_ids, output_file="transcripts.json", min_length=None):
    """Extracts transcripts using session cookies and outputs to a designated path."""
    cookie_session = load_cookies_to_session(confidential.cookie_file_path)
    min_transcript_length = min_length if min_length is not None else getattr(confidential, 'transcript_length', 500)
    
    if not cookie_session:
        print("Failed to initialize session. Aborting.")
        return

    ytt_api = YouTubeTranscriptApi(http_client=cookie_session)
    results = []

    for v_id in video_ids:
        try:
            # Respectful delay to prevent anti-bot tracking
            wait_time = random.uniform(5, 10)
            print(f"Waiting {wait_time:.2f}s before processing {v_id}...")
            time.sleep(wait_time) 
            
            # Attempt to fetch primary language
            fetched = ytt_api.fetch(v_id, languages=confidential.language)
            text = " ".join([snippet.text for snippet in fetched])
            
            # Fallback to auto-generated if transcript is too short or missing
            if len(text) < min_transcript_length:
                transcript_list = ytt_api.list(video_id=v_id)
                try:
                    auto_transcript = transcript_list.find_generated_transcript(confidential.language + ['en'])
                    data = auto_transcript.fetch()
                    text = " ".join([snippet['text'] for snippet in data])
                except Exception:
                    print(f"No suitable transcript found for {v_id}")

            results.append({
                "VideoID": v_id, 
                "Transcript": text,
                "URL": f"https://youtu.be/{v_id}"
            })
            print(f"Success: {v_id}")
            
        except Exception as e:
            print(f"Failed {v_id}: {str(e)[:100]}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

# --- Operational Execution ---

if __name__ == "__main__":
    # Fallback to local test query if executed directly instead of via orchestrator
    fallback_query = getattr(confidential, 'yt_query', "(Guru Peyarchi | குரு பெயர்ச்சி) 2026 (Thulam | துலாம்)")
    print(f"Running standalone test search for: {fallback_query}")
    
    top_video_ids = get_latest_videos(fallback_query)

    if top_video_ids:
        print(f"Found {len(top_video_ids)} videos. Starting transcript extraction...")
        pipeline_to_json_with_cookies(top_video_ids, "transcripts.json")
        print("Process complete. Transcripts saved to 'transcripts.json'.")
    else:
        print("No videos found for the given query.")