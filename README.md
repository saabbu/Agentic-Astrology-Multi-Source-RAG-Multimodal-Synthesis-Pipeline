Agentic Astrology: Multi-Source RAG & Multimodal Synthesis Pipeline
An automated end-to-end pipeline that extracts Vedic astrology forecasts from diverse YouTube sources, synthesizes them using a local LLM (Gemma 3), and generates high-fidelity multimodal outputs including Chirp3-HD audio and AI avatar videos.

🚀 The Pipeline Architecture
The system operates as a five-stage agentic workflow:

Context Extraction: Scrapes Tamil/English transcripts from top-performing YouTube astrology channels using the YouTube Data API and youtube-transcript-api with session-handling for robust retrieval.

Map-Reduce Synthesis: * Map Stage: A local Gemma 3:12b model (via Ollama) extracts specific predictions (Health, Career, Remedies) from each source.

Reduce Stage: The model synthesizes disparate viewpoints into a single, cohesive narrative in high-quality Tamil.

High-Fidelity TTS: Utilizes Google Cloud Text-to-Speech (Chirp3-HD) to generate natural, expressive Tamil narration.

Audio Engineering: Automatically layers the narration over traditional background scores (e.g., Raag Hamsadhwani) using FFmpeg and pydub, with automated ducking and looping logic.

Digital Avatar Generation: Integrates with the HeyGen API to render a lip-synced digital avatar presenting the final forecast.

🛠️ Tech Stack
Language: Python 3.10+

LLM: Gemma 3:12b (Ollama)

Cloud Services: Google Cloud (TTS), YouTube Data API v3, HeyGen API

Media Processing: FFmpeg, Pydub

Data Handling: Pandas, JSON

📂 Repository Structure
Plaintext
├── runYTTranscript.py      # Multi-source transcript scraper
├── getGemmaSummary.py      # Map-Reduce LLM synthesis logic
├── getAudioCloud.py        # Google Chirp3-HD synthesis
├── mixAudio.py             # FFmpeg-based audio mixing engine
├── getavtarVideo.py        # HeyGen avatar orchestration
├── confidential.py.sample  # Configuration template
└── requirements.txt        # Dependency manifest
⚙️ Setup & Installation
Clone the repository:

Bash
git clone https://github.com/saabbu/Agentic-Astrology-Multi-Source-RAG-Multimodal-Synthesis-Pipeline.git
cd agentic-astrology
Install Dependencies:

Bash
pip install -r requirements.txt
Install FFmpeg:
Ensure FFmpeg is installed on your system and the bin folder is added to your System PATH to enable audio mixing capabilities.

Configuration:

Rename confidential.py.sample to confidential.py.

Input your API keys for YouTube, Google Cloud, and HeyGen.

Place your Google Cloud service account JSON in the root directory.

🛠️ Usage
Run the pipeline sequentially or import modules into a controller script:

Bash
python runYTTranscript.py  # Fetch transcripts
python getGemmaSummary.py  # Synthesize narrative
python getAudioCloud.py    # Generate HD Audio
python mixAudio.py         # Mix with background score
🛡️ Security
This project uses a strict .gitignore and confidential.py architecture to ensure no API keys, session cookies, or personal credentials are ever committed to version control.

Developed as a technical exploration of Agentic RAG and Multimodal AI integration.