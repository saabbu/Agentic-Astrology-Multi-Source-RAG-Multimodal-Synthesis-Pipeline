import json
import requests
import confidential

OLLAMA_URL = confidential.ollama_url


def process_with_gemma(prompt):
    payload = {
        "model": confidential.model_name,
        "prompt": prompt,
        "stream": False,
        "options": confidential.options
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response")

def iterative_summary_pipeline(json_file="transcripts.json"):
    with open(json_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)

    individual_summaries = []
    
    # --- STAGE 1: MAP (Summarize each transcript) ---
    for i, v in enumerate(videos):
        if len(v['Transcript']) < confidential.transcript_length: continue
        
        print(f"Processing transcript {i+1}/10: {v['VideoID']}...")
        map_prompt = confidential.map_prompt.format(
            rasi=confidential.rasi,
            transit=confidential.transit,
            transcript=v['Transcript']
        )
        map_prompt = confidential.map_prompt
        summary = process_with_gemma(map_prompt)
        individual_summaries.append(summary)

    # --- STAGE 2: REDUCE (Synthesize individual summaries) ---
    print("Synthesizing final generalized summary...")
    combined_summaries = "\n\n".join(individual_summaries)
    
    reduce_prompt = confidential.reduce_prompt.format(
        rasi=confidential.rasi,
        transit=confidential.transit,
        greeting=confidential.greeting,
        combined_summaries=combined_summaries
    )
    
    final_output = process_with_gemma(reduce_prompt)
    
    with open("final_astrology_narrative.txt", "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print("Final generalized summary saved to final_astrology_narrative.txt")

iterative_summary_pipeline()