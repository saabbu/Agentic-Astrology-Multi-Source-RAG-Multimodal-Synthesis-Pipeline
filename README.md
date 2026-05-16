# Agentic Astrology: Stateful Graph Orchestration & Multimodal Synthesis Pipeline

An automated, end-to-end production pipeline that extracts Vedic astrology forecast data from multiple YouTube channels, processes it through a local Map-Reduce synthesis engine with an autonomous self-healing critique layer, and outputs high-fidelity multimodal assets (Google Chirp3-HD audio and lip-synced HeyGen digital avatar videos) sequentially across all 12 moon signs.

This branch refactors the sequential pipeline into a stateful, cyclic directed graph using **LangGraph**, formalizing error checking, retries, and state caching within a deterministic state machine.

## 🚀 Pipeline Architecture

The workflow is governed by a compiled state machine (`graph_orchestrator.py`) managing a centralized `PipelineState` object across the following phases:

1. **Workspace Folder Segregation:** Dynamically maps and isolates intermediate workspace components into `/transcripts` and `/outputs` folders based on distinct sign slugs to prevent data collisions during sequential execution loops.
2. **Context Extraction Node:** Scrapes Tamil/English transcripts using the YouTube Data API v3 and `youtube-transcript-api` via session-handling cookies to bypass bot-detection rate limits.
3. **Map-Reduce Synthesis Node (Gemma 3:12b):** * **Map Stage:** Extracts localized prediction data (Job, Business, Health, Family, Education, Remedies) from each collected video source.
   * **Reduce Stage:** Synthesizes competing and overlapping viewpoints into a structured broadcast script composed of exactly 6 sequential paragraphs to maintain topical grouping.
4. **Autonomous Audit & Correction Loop (Conditional Routing):** * **Judge Node:** Evaluates the narrative against strict layout, translation, and tone constraints, generating a numeric **Defect Score**.
   * **Conditional Edge (Evaluation Gate):** Evaluates the Defect Score trend. If the text is clean (Score = 0), it routes to asset generation. If defects remain, it routes to the **Correction Node** (up to 3 retries). If generation stagnates or degrades, a circuit breaker terminates the loop and rolls back the state to the **historical best cached script**.
5. **Media Engineering Node:** Streams the final verified text through the Google Cloud Text-to-Speech API using the native `ta-IN-Chirp3-HD-Achird` model, then layers the vocal track over background audio files using `pydub` and system **FFmpeg** binaries.
6. **Digital Avatar Production Node:** Transmits mixed audio tracks to the HeyGen API v2 endpoints to queue, poll, and log lip-synced avatar presentations.

## 📂 Repository Structure

```plaintext
├── transcripts/          # Auto-created; holds raw scraped transcript JSONs
├── outputs/              # Auto-created; holds text scripts and mixed audio
├── graph_orchestrator.py # Master controller defining the LangGraph state machine, nodes, and edges
├── runYTTranscript.py    # Stateless multi-source transcript scraper and cookie handler
├── getGemmaSummary.py    # Stateless module containing isolated Map, Reduce, and Judge execution blocks
├── getAudioCloud.py      # Google Cloud Chirp3-HD vocal synthesis engine
├── mixAudio.py           # FFmpeg and pydub audio engineering module
├── getavtarVideo.py      # HeyGen digital avatar API orchestration wrapper
├── confidential.py.sample# Centralized configuration template for API credentials and sign matrices
└── requirements.txt      # Dependency manifest specifying langgraph tracking components