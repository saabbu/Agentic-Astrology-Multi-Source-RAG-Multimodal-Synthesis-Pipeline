from gtts import gTTS
import os

# 1. Load the synthesized Tamil narrative
with open("final_astrology_narrative.txt", "r", encoding="utf-8") as f:
    mytext = f.read()

# 2. Initialize gTTS for Tamil ('ta')
# 'slow=False' ensures a natural reading speed
tts = gTTS(text=mytext, lang='ta', slow=False)

# 3. Save the output
tts.save("astrology_forecast_google.mp3")

print("Audio generated: astrology_forecast_google.mp3")