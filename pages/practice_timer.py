import requests
import io
import time
import sqlite3
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# ✅ Page Config
st.set_page_config(page_title="Practice Timer", layout="wide")

# ✅ Authentication Check
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/profile.py")

# ✅ Hide Streamlit system UI elements only
st.markdown("""
    <style>
        header, footer, #MainMenu {visibility: hidden;}
        [data-testid="stSidebarNav"] {display: none;}  /* Hides default page links */
    </style>
""", unsafe_allow_html=True)

# ✅ Custom sidebar nav
with st.sidebar:
    st.markdown("### 🧠 AI Debate Coach")
    st.page_link("main.py", label="🏠 Home")
    st.page_link("pages/history.py", label="📜 History")
    st.page_link("pages/leaderboard.py", label="🏆 Leaderboard")
    st.page_link("pages/motion_ai.py", label="💡 Motion AI")
    st.page_link("pages/practice_timer.py", label="⏱️ Practice Timer")
    st.page_link("pages/real_debate_timer.py", label="🕒 Real Debate")
    st.page_link("pages/settings.py", label="⚙️ Settings")
    st.page_link("pages/dashboard.py", label="👤 Profile")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_email"] = ""
        st.rerun()

# ✅ Optional: Back Button
if st.button("🔙 Back to Home"):
    st.switch_page("main.py")

# ✅ Timer Setup
if "time_left" not in st.session_state:
    st.session_state.time_left = 180
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_paused" not in st.session_state:
    st.session_state.timer_paused = False
if "argument_mode" not in st.session_state:
    st.session_state.argument_mode = None

# ✅ Backend API
BACKEND_URL = "http://127.0.0.1:5000"

st.title("⏳ Practice Debate Mode")
timer_duration = st.number_input("Set Timer (Minutes):", min_value=1, max_value=10, value=3, step=1)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶️ Start Timer"):
        st.session_state.time_left = timer_duration * 60
        st.session_state.timer_running = True
        st.session_state.timer_paused = False

with col2:
    if st.button("⏸️ Pause/Resume"):
        st.session_state.timer_paused = not st.session_state.timer_paused

with col3:
    if st.button("🔄 Reset Timer"):
        st.session_state.timer_running = False
        st.session_state.time_left = timer_duration * 60
        st.session_state.timer_paused = False

# ✅ Display Time
mins, secs = divmod(st.session_state.time_left, 60)
st.markdown(f"### ⏳ Time Left: {mins}:{secs:02d}")

# ✅ Countdown
if st.session_state.timer_running and not st.session_state.timer_paused:
    time.sleep(1)
    st.session_state.time_left -= 1

    if st.session_state.time_left <= 0:
        st.session_state.timer_running = False
        st.success("⏰ Time's up! Great job!")

        # Save to DB
        email = st.session_state.get("user_email", "")
        time_used = timer_duration * 60
        if email:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usage (email, practice_time)
                VALUES (?, ?)
                ON CONFLICT(email) DO UPDATE SET practice_time = practice_time + ?
            """, (email, time_used, time_used))
            conn.commit()
            conn.close()

        time.sleep(2)
        st.rerun()
    else:
        st.rerun()

# ✅ Input Mode
st.markdown("### 🎤 How will you submit your argument?")
col1, col2 = st.columns(2)
with col1:
    if st.button("🎤 Record Argument"):
        st.session_state.argument_mode = "record"
with col2:
    if st.button("✏️ Type Argument"):
        st.session_state.argument_mode = "type"

# ✅ Input Handler
user_input = ""
if st.session_state.argument_mode == "record":
    st.subheader("🎙️ Speak your argument")
    audio_bytes = audio_recorder()
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.success("✅ Recording complete! Processing...")

        with st.spinner("🔍 Converting speech to text..."):
            try:
                files = {"file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")}
                response = requests.post(f"{BACKEND_URL}/speech-to-text", files=files, timeout=10)
                response.raise_for_status()
                st.session_state.transcribed_text = response.json().get("transcription", "")
            except:
                st.error("❌ Failed to transcribe audio.")

if st.session_state.argument_mode == "type":
    st.subheader("📝 Type Your Argument")
    user_input = st.text_area(" ", value=st.session_state.get("transcribed_text", ""), placeholder="Enter your argument here...")

# ✅ Text-to-Speech
if user_input or st.session_state.get("transcribed_text"):
    if st.button("🔊 AI Reads Argument"):
        st.subheader("🔊 AI Text-to-Speech")
        with st.spinner("🔊 Processing..."):
            try:
                tts_response = requests.post(f"{BACKEND_URL}/text-to-speech", json={"text": user_input or st.session_state.transcribed_text})
                tts_response.raise_for_status()
                st.audio(tts_response.content, format="audio/mp3")
            except:
                st.error("❌ Failed to convert to speech.")

st.divider()

# ✅ Evaluate Argument
if st.button("✅ Evaluate Argument"):
    final_argument = user_input.strip() if user_input else st.session_state.get("transcribed_text", "").strip()

    if not final_argument:
        st.error("❌ No argument provided.")
    else:
        with st.spinner("🔍 Evaluating..."):
            try:
                response = requests.post(f"{BACKEND_URL}/evaluate-argument", json={"topic": st.session_state.get("topic", ""), "text": final_argument}, timeout=10)
                result = response.json()
                st.session_state.rationality_score = result.get("rationality_score")
                st.session_state.reason_for_score = result.get("reason_for_score")
                st.session_state.feedback = result.get("feedback")
            except:
                st.error("❌ AI Evaluation failed.")

# ✅ Feedback Output
if st.session_state.get("rationality_score") is not None:
    st.markdown("### 📊 AI Feedback")
    st.write(f"🔹 **Rationality Score:** {st.session_state.rationality_score}/100")
    st.write(f"🔹 **Strengths:** {st.session_state.reason_for_score}")
    st.write(f"🔹 **Weaknesses:** {st.session_state.feedback}")

