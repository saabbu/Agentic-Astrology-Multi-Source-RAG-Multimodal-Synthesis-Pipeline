from pydub import AudioSegment
import confidential
import os

ffmpeg_bin_path = confidential.ffmpeg_path

AudioSegment.converter = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_bin_path, "ffprobe.exe")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

def mix_astrology_audio(lead_track=None, output_track=None):
    # Set execution fallbacks if called natively without loop variables
    input_lead = lead_track if lead_track else confidential.narration_lead_audio
    output_mix = output_track if output_track else confidential.final_output_file
    
    print(f"Loading files: Lead -> {input_lead} | Background -> {confidential.background_music_audio}")
    
    narration = AudioSegment.from_file(input_lead)
    background = AudioSegment.from_file(confidential.background_music_audio)

    # Adjust background volume
    background = background + confidential.bg_music_volume_db

    # Loop the background track to match narration length
    loop_count = int(len(narration) / len(background)) + 1
    background_looped = background * loop_count

    # Overlay and crop to narration length
    final_mix = narration.overlay(background_looped, position=0)

    final_mix.export(output_mix, format="mp3")
    print(f"Mixing complete! Saved as: {output_mix}")

if __name__ == "__main__":
    mix_astrology_audio()