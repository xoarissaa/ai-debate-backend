import streamlit as st
import requests
import io
from pydub import AudioSegment

st.title("🎤 AI Powered Debate Coach")

# Set backend URL for Railway deployment
BACKEND_URL = "ai-debate-coach-production.up.railway.app"  # Replace with your actual Railway backend URL

# Initialize session state variables
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "reason_for_score" not in st.session_state:
    st.session_state.reason_for_score = ""
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "rationality_score" not in st.session_state:
    st.session_state.rationality_score = None

# **Text Input for Debate Topic**
st.subheader("🎯 Debate Topic")
st.session_state.topic = st.text_input(" ", st.session_state.topic, placeholder="Enter the topic of your argument here...")

st.subheader("📝 Your Argument")

# **Record Audio**
audio_bytes = st.audio("", format="audio/wav", start_time=0)  # Placeholder for Streamlit's audio input
uploaded_audio = st.file_uploader("🎙 Record or upload your argument", type=["wav"])

if uploaded_audio:
    st.success("✅ Recording complete! Processing...")

    # Convert uploaded file to the correct format
    audio = AudioSegment.from_file(uploaded_audio, format="wav")
    audio_buffer = io.BytesIO()
    audio.export(audio_buffer, format="wav")
    audio_buffer.seek(0)

    # Send audio to backend for speech-to-text conversion
    response = requests.post(f"{BACKEND_URL}/speech-to-text", files={"file": audio_buffer})

    if response.status_code == 200:
        st.session_state.transcribed_text = response.json().get("transcription", "")
    else:
        st.error("❌ Failed to process speech. Try again.")

# **Text Area for Editing Argument**
user_input = st.text_area(" ", st.session_state.transcribed_text, placeholder="Enter or edit your argument here...")
evaluate_button = st.button("✅ Evaluate Argument")

st.divider()

# **Submit Button for AI Evaluation**
if evaluate_button:
    final_argument = user_input if user_input.strip() else st.session_state.transcribed_text  # Use typed text if available

    # **Show loading spinner while AI processes**
    with st.spinner("🔍 Analyzing your argument..."):
        response = requests.post(f"{BACKEND_URL}/evaluate-argument", json={"topic": st.session_state.topic, "text": final_argument})

    if response.status_code == 200:
        result = response.json()
        st.session_state.rationality_score = result.get("rationality_score", None)
        st.session_state.reason_for_score = result.get("reason_for_score", "No reasoning provided.")
        st.session_state.feedback = result.get("feedback", "No feedback provided.")
    
    elif response.status_code == 400:  # Handle Gemini's blocked response
        st.session_state.feedback = "⚠️ AI could not generate a response due to content restrictions. Please rephrase your argument."

    else:
        st.session_state.feedback = "❌ AI evaluation failed."

# **Display Rationality Score (Next to Subheading)**
if st.session_state.rationality_score is not None:
    st.subheader(f"📊 Rationality Score: {st.session_state.rationality_score:.2f}")
    st.progress(st.session_state.rationality_score)

    # Display reason for score below the meter
    if st.session_state.reason_for_score:
        st.write(f"📝 *{st.session_state.reason_for_score}*")

# **Display AI Feedback (Without Rationality Score)**
if st.session_state.feedback:
    st.subheader("🤖 AI Feedback:")
    st.write(st.session_state.feedback)
