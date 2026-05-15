# Agentic Astrology: Multi-Sign Automated Loop Engine & Multimodal Synthesis Pipeline

An automated, end-to-end production pipeline that extracts Vedic astrology forecast data from multiple YouTube channels, processes it through a local Map-Reduce synthesis engine with an autonomous self-healing critique layer, and outputs high-fidelity multimodal assets (Google Chirp3-HD audio and lip-synced HeyGen digital avatar videos) sequentially across all 12 moon signs.

## 🚀 Pipeline Architecture

The engine operates via a centralized orchestration loop executed sequentially for every sign defined in the execution matrix:

1. **Workspace Folder Segregation & Path Isolation:** To prevent file cross-over and synchronization data overwrites during loop steps, the system dynamically maps and isolates intermediate workspace components into `/transcripts` and `/outputs` folders based on distinct string slugs (e.g., `transcripts_mesham.json`).
2. **Context Extraction Loop:** Scrapes Tamil/English transcripts using the YouTube Data API v3 and `youtube-transcript-api` via session-handling cookies to bypass bot-detection rate limits. It dynamically targets queries built from English and Tamil keyword matrices.
3. **Map-Reduce Synthesis (Gemma 3:12b):**
   * **Map Stage:** Extracts localized prediction data (Job, Business, Health, Family, Education, Remedies) from each collected video source.
   * **Reduce Stage:** Synthesizes competing and overlapping viewpoints into a structured broadcast script composed of exactly 6 sequential paragraphs to maintain topical grouping.
4. **Autonomous Critique-Correction (Self-Healing Loop):** To fix formatting anomalies like markdown text headers, parenthetical dual-language translations, or tone leakage (e.g., spiritual guru postures) before paying for cloud APIs, the narrative is routed through an autonomous evaluation loop. The system checks syntax, tracks errors via a numeric Defect Score, executes up to 3 editing recycles, and systematically caches the historically optimal state to prevent empty outputs or structural degradation due to local context drift.
5. **High-Fidelity Vocal Synthesis:** Passes the clean narrative script to the Google Cloud Text-to-Speech API using the native `ta-IN-Chirp3-HD-Achird` model.
6. **Audio Engineering Layer:** Uses FFmpeg and `pydub` to adjust volume metrics, loop background tracks (e.g., Raag Hamsadhwani), and overlay voiceovers over continuous musical compositions.
7. **Digital Avatar Production:** Transmits mixed audio tracks to the HeyGen API v2 endpoints to queue, poll, and log lipsynced avatar presentations.

## 📂 Repository Structure

```plaintext
├── transcripts/            # Created automatically; holds raw scraped JSON transcripts
├── outputs/                # Created automatically; holds text narratives, voice tracks, and mixed media
├── orchestrator.py         # Main loop controller driving the end-to-end sequential pipeline
├── runYTTranscript.py      # Modular scrapper handling cookie loading and search parameters
├── getGemmaSummary.py      # Map-Reduce engine with internal critique loops and state caching
├── getAudioCloud.py        # Google Cloud TTS Chirp3-HD chunking and synthesis engine
├── mixAudio.py             # Audio engineering module interfacing with system FFmpeg tools
├── getavtarVideo.py        # HeyGen API video instantiation and status polling wrapper
├── confidential.py.sample  # Centralized template for API credentials, prompts, and sign matrix
└── requirements.txt        # Python dependency manifest