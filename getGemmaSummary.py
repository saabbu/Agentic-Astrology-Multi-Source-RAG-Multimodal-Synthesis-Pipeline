import json
import requests
import confidential

OLLAMA_URL = confidential.ollama_url

def process_with_judge(prompt):
    payload = {
        "model": confidential.judge_model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(confidential.ollama_url, json=payload)
        return json.loads(response.json().get("response", "{}"))
    except Exception as e:
        print(f"Judge connection failure: {e}")
        return {"compliance_passed": False, "failures": [f"Auditor engine timeout: {str(e)}"]}

def get_clean_bool(report, key, default_fallback):
    val = report.get(key, default_fallback)
    if isinstance(val, bool): return val
    if isinstance(val, str): return val.lower() in ['true', 'yes', '1']
    return bool(val)

def calculate_defect_score(audit_report):
    # Defensive programming check: if the list of failures is explicitly empty, force zero defects
    if isinstance(audit_report.get("failures"), list) and len(audit_report["failures"]) == 0:
        return 0
        
    score = 0
    if get_clean_bool(audit_report, "has_headings_or_labels", True): score += 1
    if get_clean_bool(audit_report, "has_bracketed_translations", True): score += 1
    if get_clean_bool(audit_report, "is_spiritual_or_preachy", True): score += 1
    if not get_clean_bool(audit_report, "compliance_passed", False): score += 1
    return score

def process_with_gemma(prompt):
    payload = {
        "model": confidential.model_name,
        "prompt": prompt,
        "stream": False,
        "options": confidential.options
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response")

def iterative_summary_pipeline(json_file="transcripts.json", output_txt="final_astrology_narrative.txt", rasi=None, transit=None, greeting=None):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)
    except Exception as e:
        print(f"Error reading transcript file {json_file}: {e}")
        return False

    individual_summaries = []
    target_rasi = rasi if rasi else confidential.rasi
    target_transit = transit if transit else confidential.transit
    target_greeting = greeting if greeting else confidential.greeting
    
    # --- STAGE 1: MAP ---
    for i, v in enumerate(videos):
        if len(v['Transcript']) < confidential.transcript_length: 
            continue
        print(f"Processing transcript {i+1}/{len(videos)}: {v['VideoID']}...")
        formatted_map_prompt = confidential.map_prompt.format(
            rasi=target_rasi, transit=target_transit, transcript=v['Transcript']
        )
        summary = process_with_gemma(formatted_map_prompt)
        individual_summaries.append(summary)

    if not individual_summaries:
        print("No valid transcripts met constraints.")
        return False

    # --- STAGE 2: REDUCE ---
    print("Synthesizing final generalized summary with topic groupings...")
    combined_summaries = "\n\n".join(individual_summaries)
    formatted_reduce_prompt = confidential.reduce_prompt.format(
        rasi=target_rasi, transit=target_transit, greeting=target_greeting, combined_summaries=combined_summaries
    )
    current_script = process_with_gemma(formatted_reduce_prompt)
    
    # --- STAGE 3: SELF-HEALING CACHING LOOP ---
    max_retries = 3
    attempt = 0
    best_script = current_script
    best_defect_score = float('inf')
    
    while attempt <= max_retries:
        print(f"\n[Audit Pass {attempt}] Evaluating layout compliance and topical structure...")
        formatted_judge_prompt = confidential.judge_prompt.format(generated_script=current_script)
        audit_report = process_with_judge(formatted_judge_prompt)
        
        current_defect_score = calculate_defect_score(audit_report)
        failures = audit_report.get("failures", [])
        
        print(f"Pass {attempt} Registered Failures: {failures}")
        print(f"Current Defect Score: {current_defect_score} (Historical Lowest: {best_defect_score})")
        
        # Immediate clean exit conditions
        if current_defect_score == 0 or (len(failures) == 0 and attempt == 0):
            print("Verification successful. Text clean of structure headings and grouping is correct.")
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(current_script)
            return True
            
        if current_defect_score < best_defect_score:
            best_defect_score = current_defect_score
            best_script = current_script
            print(f"--> Improved state cached (Defect Score: {best_defect_score})")

        if attempt == max_retries:
            print(f"Reaching iteration limit. Writing out optimal script with score {best_defect_score}.")
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(best_script)
            return True 

        if attempt > 0 and current_defect_score >= best_defect_score:
            print(f"Stagnation hit ({current_defect_score} >= {best_defect_score}). Breaking sequence to output best state.")
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(best_script)
            return True
            
        failures_str = "\n".join([f"- {f}" for f in failures])
        correction_prompt = f"""Role: You are a copyeditor removing formatting markers from news text scripts.
Task: Edit the provided text to resolve these explicit failures.

Failures to Strip:
{failures_str}

Strict Rules:
1. Maintain the 6 distinct topical paragraphs (Job, Business, Health, Family, Education, Remedies) exactly in their current blocks. Do NOT mix them together.
2. Delete all visible topic names, colons, titles, brackets, asterisks, and spiritual blessings.
3. Do not append notes like "Here is the corrected script". Return only the clean paragraphs.

Text to Clean:
{current_script}
"""
        print(f"Sending correction data to engine for Pass {attempt+1}...")
        current_script = process_with_gemma(correction_prompt)
        attempt += 1

if __name__ == "__main__":
    iterative_summary_pipeline()