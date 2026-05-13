import os
from google.cloud import texttospeech
import re

# 1. Set the path to your credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-tts-creds.json"

def clean_and_split_text(text, max_bytes=4500):
    # 1. Clean markdown and source tags
    text = text.replace("**", "")
    text = re.sub(r"\\", "", text)
    
    # 2. Split by sentences (using Tamil/English period markers)
    sentences = re.split(r'([.!?।])', text)
    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i] + sentences[i+1]
        # Check byte size of current chunk + next sentence
        if len((current_chunk + sentence).encode('utf-8')) < max_bytes:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def generate_astrology_audio(input_file="final_astrology_narrative.txt"):
    client = texttospeech.TextToSpeechClient()
    
    # List all available Tamil voices
    voices = client.list_voices(language_code="ta-IN")
    for voice in voices.voices:
        print(f"Name: {voice.name}, Gender: {voice.ssml_gender}")

    with open(input_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    text_chunks = clean_and_split_text(full_text)
    combined_audio = bytearray()

    print(f"Text split into {len(text_chunks)} chunks for processing...")

    # Configure the voice request for high-fidelity Chirp3-HD
    voice = texttospeech.VoiceSelectionParams(
        language_code="ta-IN",
        name="ta-IN-Chirp3-HD-Achird" 
    )

    # Note: Chirp3-HD voices are highly sensitive to speaking rate
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0, # Chirp models sound best at default speed
        pitch=0.0
    )

    for i, chunk in enumerate(text_chunks):
        print(f"Synthesizing chunk {i+1}...")
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        
        response = client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )
        # Append the audio content (bytes)
        combined_audio.extend(response.audio_content)

    # Save the full combined file
    with open("guru_peyarchi_2026_full.mp3", "wb") as out:
        out.write(combined_audio)
        print("Success! Audio saved to 'guru_peyarchi_2026_full.mp3'")

generate_astrology_audio()