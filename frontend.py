import streamlit as st
import requests
import os
import time
import tempfile
from pydub import AudioSegment
from pydub.playback import play

st.title("🎤 AI Debate Coach - Speech Analysis")

# Record Speech Button
st.write("Click the button below to record your speech.")
if st.button("🎙 Record Speech"):
    st.warning("Recording... Speak now!")
    
    # Simulate recording delay
    time.sleep(5)  

    # Simulated audio file (we will replace this with real recording later)
    st.success("Recording complete! Processing...")

    # Send the recorded speech to backend (dummy file for now)
    file_path = os.path.join("speech_samples", "sample.wav")
    with open(file_path, "rb") as file:
        response = requests.post("http://127.0.0.1:5000/speech-to-text", files={"file": file})

    if response.status_code == 200:
        transcription = response.json().get("transcription", "")
        st.subheader("Transcribed Speech:")
        st.write(f"📝 {transcription}")
    else:
        st.error("Failed to process speech. Try again.")
