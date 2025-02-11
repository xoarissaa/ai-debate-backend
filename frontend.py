import streamlit as st
import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import tempfile

st.title("🎤 AI Powered Debate Coach")

# Initialize session state variables
if "recording" not in st.session_state:
    st.session_state.recording = False
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "audio_data" not in st.session_state:
    st.session_state.audio_data = []
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "improved_argument" not in st.session_state:
    st.session_state.improved_argument = ""
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "rationality_score" not in st.session_state:
    st.session_state.rationality_score = None

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

def start_recording():
    """Start recording audio from the microphone."""
    st.session_state.recording = True
    st.session_state.audio_data = []  # Reset previous audio data

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.int16, callback=audio_callback):
        while st.session_state.recording:
            st.session_state.audio_data.append(audio_q.get())

def stop_recording():
    """Stop recording and process the audio."""
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

# **Text Input for Debate Topic**
st.subheader("🎯 Debate Topic")
st.session_state.topic = st.text_input("Enter the topic of your argument:", st.session_state.topic)

# **Record Button (Simple Toggle)**
if st.button("🎙 Record Argument"):
    if st.session_state.recording:
        stop_recording()
    else:
        start_recording()

# **Text Area for Editing Argument**
st.subheader("📝 Your Argument (Edit if needed)")
user_input = st.text_area("You can type directly or edit the transcribed speech:", st.session_state.transcribed_text)

# **Submit Button for AI Evaluation**
if st.button("✅ Evaluate Argument"):
    response = requests.post("http://127.0.0.1:5000/evaluate-argument", json={"topic": st.session_state.topic, "text": user_input})
    
    if response.status_code == 200:
        result = response.json()
        st.session_state.rationality_score = result["rationality_score"]
        st.session_state.feedback = result["feedback"]
    else:
        st.session_state.feedback = "❌ AI evaluation failed."

# **Display Rationality Meter (Above AI Feedback)**
if st.session_state.rationality_score is not None:
    st.subheader("📊 Rationality Meter")
    st.progress(st.session_state.rationality_score)

# **Display AI Feedback**
if st.session_state.feedback:
    st.subheader("🤖 AI Feedback & Improved Argument:")
    st.write(st.session_state.feedback)
