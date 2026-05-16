# graph_orchestrator.py
from typing import List, TypedDict
from langgraph.graph import StateGraph, END
import json
import os
import confidential

ffmpeg_bin_path = confidential.ffmpeg_path
if ffmpeg_bin_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_bin_path + os.path.pathsep + os.environ["PATH"]



# Import your existing module operations
import runYTTranscript
import getGemmaSummary
import getAudioCloud
import mixAudio


Bypass_scraping = False
# 1. Define the Shared Pipeline State
class PipelineState(TypedDict):
    slug: str
    query: str
    rasi: str
    transit: str
    greeting: str
    current_script: str
    defect_score: int
    failures: List[str]
    retry_count: int
    best_script: str
    best_defect_score: int

# 2. Define Node Execution Functions
def scrape_transcripts_node(state: PipelineState):
    json_path = f"transcripts/transcripts_{state['slug']}.json"
    video_ids = runYTTranscript.get_latest_videos(state['query'])
    runYTTranscript.pipeline_to_json_with_cookies(video_ids, output_file=json_path)
    return {}

def synthesize_narrative_node(state: PipelineState):
    json_path = f"transcripts/transcripts_{state['slug']}.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    maps = getGemmaSummary.generate_map_summaries(videos, state['rasi'], state['transit'])
    initial_script = getGemmaSummary.execute_reduce_synthesis("\n\n".join(maps), state['rasi'], state['transit'], state['greeting'])
    
    return {"current_script": initial_script, "best_script": initial_script, "retry_count": 0, "best_defect_score": 999}

def audit_script_node(state: PipelineState):
    report = getGemmaSummary.execute_script_audit(state['current_script'])
    
    # Calculate defect score based on clean bool helper parameters
    score = 0
    failures = report.get("failures", [])
    if len(failures) > 0:
        if report.get("has_headings_or_labels"): score += 1
        if report.get("has_bracketed_translations"): score += 1
        if report.get("is_spiritual_or_preachy"): score += 1
        if not report.get("compliance_passed"): score += 1
    
    updates = {"defect_score": score, "failures": failures}
    if score < state['best_defect_score']:
        updates["best_defect_score"] = score
        updates["best_script"] = state['current_script']
        
    return updates

def correct_script_node(state: PipelineState):
    corrected = getGemmaSummary.execute_correction_pass(state['current_script'], state['failures'])
    return {"current_script": corrected, "retry_count": state['retry_count'] + 1}

def generate_assets_node(state: PipelineState):
    # Determine the clean script source (exact pass or historical fallback snapshot)
    final_text = state['best_script']
    narrative_path = f"outputs/narrative_{state['slug']}.txt"
    lead_audio = f"outputs/lead_{state['slug']}.mp3"
    mixed_audio = f"outputs/astrology_mix_{state['slug']}.mp3"
    
    with open(narrative_path, "w", encoding="utf-8") as f:
        f.write(final_text)
        
    getAudioCloud.generate_astrology_audio(input_file=narrative_path, output_mp3=lead_audio)
    mixAudio.mix_astrology_audio(lead_track=lead_audio, output_track=mixed_audio)
    return {}

# 3. Define Conditional Routing Edge Logic
def evaluation_gate(state: PipelineState):
    if state["defect_score"] == 0:
        return "perfect_pass"
    if state["retry_count"] >= 3 or state["defect_score"] > state["best_defect_score"]:
        return "stagnated_or_maxed"
    return "try_correction"

# 4. Construct and Compile the LangGraph
workflow = StateGraph(PipelineState)

workflow.add_node("scrape", scrape_transcripts_node)
workflow.add_node("synthesize", synthesize_narrative_node)
workflow.add_node("audit", audit_script_node)
workflow.add_node("correct", correct_script_node)
workflow.add_node("generate_assets", generate_assets_node)

if Bypass_scraping:
    workflow.set_entry_point("synthesize")
else:
    workflow.set_entry_point("scrape")
    workflow.add_edge("scrape", "synthesize")
workflow.add_edge("synthesize", "audit")

workflow.add_conditional_edges(
    "audit",
    evaluation_gate,
    {
        "perfect_pass": "generate_assets",
        "stagnated_or_maxed": "generate_assets",
        "try_correction": "correct"
    }
)
workflow.add_edge("correct", "audit")
workflow.add_edge("generate_assets", END)

app = workflow.compile()

if __name__ == "__main__":
    # Ensure local directory workspace separation exists
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    # Verify the presence of the execution matrix inside configuration
    if hasattr(confidential, "SEARCH_CRITERIA_LIST"):
        for criteria in confidential.SEARCH_CRITERIA_LIST:
            print(f"\n==================================================")
            print(f"Initializing LangGraph Pipeline for: {criteria['rasi']}")
            print(f"==================================================")
            
            # Seed the initial state fields for the current sign partition
            initial_state = {
                "slug": criteria["slug"],
                "query": criteria["query"],
                "rasi": criteria["rasi"],
                "transit": criteria["transit"],
                "greeting": criteria["greeting"],
                "current_script": "",
                "defect_score": 999,
                "failures": [],
                "retry_count": 0,
                "best_script": "",
                "best_defect_score": 999
            }
            
            try:
                # Trigger the runtime execution of the compiled graph state machine
                final_state = app.invoke(initial_state)
                print(f"--> Sequence complete for {criteria['rasi']}.")
                print(f"--> Final Logged Defect Score: {final_state.get('best_defect_score')}")
            except Exception as e:
                print(f"Execution failure on sign partition {criteria['slug']}: {str(e)}")
    else:
        print("Execution halted: SEARCH_CRITERIA_LIST array definition missing from confidential.py.")