# orchestrator.py
import os
import confidential
from runYTTranscript import get_latest_videos, pipeline_to_json_with_cookies
from getGemmaSummary import iterative_summary_pipeline
from getAudioCloud import generate_astrology_audio
from mixAudio import mix_astrology_audio
from getavtarVideo import generate_avatar_video

SEARCH_CRITERIA_LIST = confidential.SEARCH_CRITERIA_LIST
skip_scraping = True

def run_pipeline():
    # Enforce strict directory isolation for generated data assets
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    for criteria in SEARCH_CRITERIA_LIST:
        slug = criteria["slug"]
        query = criteria["query"]
        rasi = criteria["rasi"]
        transit = criteria["transit"]
        greeting = criteria["greeting"]
        
        print(f"\n==================================================")
        print(f"PROCESSING TARGET RASI: {slug.upper()}")
        print(f"==================================================")
        
        # Explicit namespacing to eliminate collision and loop data overwrites
        json_output = os.path.join("transcripts", f"transcripts_{slug}.json")
        narrative_output = os.path.join("outputs", f"narrative_{slug}.txt")
        lead_audio_output = os.path.join("outputs", f"lead_{slug}.mp3")
        final_mixed_audio = os.path.join("outputs", f"astrology_mix_{slug}.mp3")
        
        # Step 1: Automated Transcript Scraping
        print(f"[1/5] Extracting source transcripts -> {json_output}")
        if (not skip_scraping):
            video_ids = get_latest_videos(query)
            if not video_ids:
                print(f"Skipping {slug}: No target videos resolved by YouTube Data API.")
                continue
            pipeline_to_json_with_cookies(video_ids, output_file=json_output)
        
        # Step 2: Synthesis and Multi-Turn Compliance Audit
        print(f"[2/5] Synthesizing consensus and running self-healing auditor loop...")
        # Catches the definitive pass/fail boolean from getGemmaSummary
        pipeline_viable = iterative_summary_pipeline(
            json_file=json_output, 
            output_txt=narrative_output,
            rasi=rasi,
            transit=transit,
            greeting=greeting
        )
        
        # Circuit Breaker: Halt only if no viable narrative could be generated or saved
        if not pipeline_viable:
            print(f"CRITICAL ERROR: {slug.upper()} processing failed. Halting chain to preserve downstream API budget.")
            continue
            
        print(f"PROCEEDING: Viable narrative file locked for {slug.upper()}. Commencing asset generation.")
        
        # Step 3: Vocal Track Rendering (Google Cloud TTS Call)
        print(f"[3/5] Requesting Google Cloud Chirp3-HD synthesis -> {lead_audio_output}")
        generate_astrology_audio(input_file=narrative_output, output_mp3=lead_audio_output)
        
        # Step 4: Music Overlay and Audio Engineering (Local FFmpeg Process)
        print(f"[4/5] Running audio mixing engine -> {final_mixed_audio}")
        mix_astrology_audio(lead_track=lead_audio_output, output_track=final_mixed_audio)
        
        # Step 5: Digital Avatar Production (HeyGen API Queue)
        # print(f"[5/5] Transmitting final mixed audio track to HeyGen Avatar API...")
        # video_url = generate_avatar_video(final_mixed_audio)
        
        # if video_url:
        #     print(f"SUCCESS: Completed full pipeline production loop for {slug.upper()}.")
        #     print(f"Rendered Asset URL: {video_url}")
        #     with open(os.path.join("outputs", "completed_production_log.txt"), "a") as log:
        #         log.write(f"{slug}: {video_url}\n")
        # else:
        #     print(f"WARNING: HeyGen asset generation dropped or failed for {slug.upper()}.")

if __name__ == "__main__":
    run_pipeline()