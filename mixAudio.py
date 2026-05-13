from pydub import AudioSegment
import confidential
import os

# 1. Update this path to the EXACT folder where you extracted ffmpeg
# It must point to the 'bin' folder containing ffmpeg.exe and ffprobe.exe
ffmpeg_bin_path = confidential.ffmpeg_path

# 2. Assign the engines to pydub
AudioSegment.converter = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_bin_path, "ffprobe.exe")

# 3. Also add to system path for this session to be safe
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

def mix_astrology_audio():
    print("Loading audio files...")
    # 1. Load the narration and background tracks
    print (confidential.narration_lead_audio)
    narration = AudioSegment.from_file(confidential.narration_lead_audio)
    background = AudioSegment.from_file(confidential.background_music_audio)

    # 2. Adjust background volume
    # We apply the reduction defined in configuration
    background = background + confidential.bg_music_volume_db

    # 3. Loop the background to match narration length
    # If background is shorter, it repeats. If longer, it will be sliced during overlay.
    loop_count = int(len(narration) / len(background)) + 1
    background_looped = background * loop_count

    # 4. Overlay the tracks
    # The 'position=0' starts the overlay at the beginning
    # The length is automatically capped to the length of the 'narration' track
    final_mix = narration.overlay(background_looped, position=0)

    # 5. Export the final product
    final_mix.export(confidential.final_output_file, format="mp3")
    print(f"Mixing complete! Saved as: {confidential.final_output_file}")

if __name__ == "__main__":
    mix_astrology_audio()