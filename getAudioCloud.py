import os
from google.cloud import texttospeech
import re

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-tts-creds.json"

def clean_and_split_text(text, max_bytes=4500):
    text = text.replace("**", "")
    text = re.sub(r"\\", "", text)
    
    sentences = re.split(r'([.!?।])', text)
    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i] + sentences[i+1]
        if len((current_chunk + sentence).encode('utf-8')) < max_bytes:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def generate_astrology_audio(input_file="final_astrology_narrative.txt", output_mp3="guru_peyarchi_2026_full.mp3"):
    client = texttospeech.TextToSpeechClient()

    with open(input_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    text_chunks = clean_and_split_text(full_text)
    combined_audio = bytearray()

    print(f"Text split into {len(text_chunks)} chunks for processing...")

    voice = texttospeech.VoiceSelectionParams(
        language_code="ta-IN",
        name="ta-IN-Chirp3-HD-Achird" 
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0, 
        pitch=0.0
    )

    for i, chunk in enumerate(text_chunks):
        print(f"Synthesizing chunk {i+1}/{len(text_chunks)}...")
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        
        response = client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )
        combined_audio.extend(response.audio_content)

    with open(output_mp3, "wb") as out:
        out.write(combined_audio)
        print(f"Success! Audio saved to '{output_mp3}'")

if __name__ == "__main__":
    generate_astrology_audio()