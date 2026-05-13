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

# --- Configuration ---
ytclient = build('youtube', 'v3', developerKey=confidential.yt_google_api_key)
yt_query = confidential.yt_query
min_transcript_length = confidential.transcript_length
date_time_lookout = confidential.date_time_lookout
primary_lang = confidential.language[0] if confidential.language else 'ta'

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

def get_latest_videos(query):
    """Fetches recent video IDs based on relevance and duration."""
    timelimit = (datetime.now() - timedelta(days=date_time_lookout)).isoformat() + 'Z'
    
    request = ytclient.search().list(
        q=query,
        part='snippet',
        maxResults=confidential.max_results,
        type='video',
        videoDuration='medium',
        order='relevance',
        publishedAfter=timelimit,
        relevanceLanguage=primary_lang
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response['items']]

# --- Extraction Pipeline ---

def pipeline_to_json_with_cookies(video_ids, output_file="transcripts.json"):
    """Extracts transcripts using session cookies to prevent blocking."""
    cookie_session = load_cookies_to_session(confidential.cookie_file_path)
    
    if not cookie_session:
        print("Failed to initialize session. Aborting.")
        return

    ytt_api = YouTubeTranscriptApi(http_client=cookie_session)
    results = []

    for v_id in video_ids:
        try:
            # Respectful delay for safety
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
    print(f"Searching for: {yt_query}")
    top_video_ids = get_latest_videos(yt_query)

    if top_video_ids:
        print(f"Found {len(top_video_ids)} videos. Starting transcript extraction...")
        pipeline_to_json_with_cookies(top_video_ids)
        print("Process complete. Transcripts saved to 'transcripts.json'.")
    else:
        print("No videos found for the given query.")