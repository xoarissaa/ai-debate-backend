import streamlit as st
import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import tempfile

st.title("🎤 AI Debate Coach - Speech Analysis")

# Initialize session state variables if not set
if "recording" not in st.session_state:
    st.session_state.recording = False
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "audio_data" not in st.session_state:
    st.session_state.audio_data = []

# Queue to store recorded audio in real-time
audio_q = queue.Queue()

# Audio settings
SAMPLE_RATE = 44100  # CD-quality
CHANNELS = 1  # Mono audio

def audio_callback(indata, frames, time, status):
    """Callback function to continuously store recorded audio in queue."""
    if status:
        print(status)
    audio_q.put(indata.copy())

def toggle_recording():
    """Start or stop recording based on the current state (without background threads)."""
    if not st.session_state.recording:
        # Start recording
        st.session_state.recording = True
        st.session_state.audio_data = []  # Reset previous audio data

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.int16, callback=audio_callback):
            st.info("🎙 Recording... Click the button to stop.")
            while st.session_state.recording:
                st.session_state.audio_data.append(audio_q.get())
    else:
        # Stop recording
        st.session_state.recording = False
        st.success("✅ Recording complete! Processing...")

        # Convert recorded chunks into a NumPy array
        if len(st.session_state.audio_data) > 0:
            audio_array = np.concatenate(st.session_state.audio_data, axis=0)

            # Save the audio as a WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                wav.write(temp_file.name, SAMPLE_RATE, audio_array)
                file_path = temp_file.name

            # Send the properly formatted WAV file to the Flask backend for speech-to-text conversion
            with open(file_path, "rb") as file:
                response = requests.post("http://127.0.0.1:5000/speech-to-text", files={"file": file})

            if response.status_code == 200:
                st.session_state.transcribed_text = response.json().get("transcription", "")
            else:
                st.error("❌ Failed to process speech. Try again.")

# **Toggle Button (Works in One Click)**
clicked = st.button("🛑 Stop Recording" if st.session_state.recording else "🎙 Start Recording")

if clicked:
    toggle_recording()
    st.rerun()  # Instantly refresh UI (Fixed method)

# Text Input (Editable)
st.subheader("📝 Your Argument (Edit if needed)")
user_input = st.text_area("You can type directly or edit the transcribed speech:", st.session_state.transcribed_text)

# Submit Button
if st.button("✅ Submit Argument"):
    st.success("Argument submitted for analysis! (Feature coming in later phases)")
