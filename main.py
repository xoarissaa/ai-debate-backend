import streamlit as st
import requests
import io
from audio_recorder_streamlit import audio_recorder

# ✅ Page config & hide default Streamlit nav
st.set_page_config(page_title="AI Debate Coach", page_icon="🧠", layout="wide")

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

# ✅ Auth check
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/profile.py")

# ✅ Backend
BACKEND_URL = "https://ai-debate-backend.onrender.com"

# ✅ Init state
for key in ["topic", "transcribed_text", "feedback", "reason_for_score", "rationality_score"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "rationality_score" else None

# 🧠 Page title
st.title("📝 Evaluate Your Argument")

# 🎯 Topic input
st.markdown("#### 🎯 Topic")
st.session_state.topic = st.text_input(
    "Enter the topic of your argument",
    st.session_state.topic,
    placeholder="e.g. Should AI replace teachers?"
)

# 🎙️ Audio input
st.markdown("#### 🎙️ Record Your Argument")
audio_bytes = audio_recorder(text="Click to record", icon_size="2x")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.success("✅ Recording captured! Converting to text...")
    with st.spinner("Converting speech to text..."):
        try:
            files = {"file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")}
            response = requests.post(f"{BACKEND_URL}/speech-to-text", files=files, timeout=30)
            response.raise_for_status()
            st.session_state.transcribed_text = response.json().get("transcription", "")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {str(e)}")
        except ValueError:
            st.error("❌ Invalid server response.")

# ✏️ Argument input
st.markdown("#### ✏️ Edit or Type Your Argument")
user_input = st.text_area(
    "Argument text",
    st.session_state.transcribed_text,
    height=200,
    placeholder="Type or edit your argument here..."
)

# ✅ Evaluate button
evaluate_button = st.button("✅ Evaluate Argument", use_container_width=True)

# 🔍 Evaluation logic
if evaluate_button:
    if not st.session_state.topic.strip():
        st.error("❌ Please enter a topic.")
    elif not user_input.strip():
        st.error("❌ Argument text is empty.")
    else:
        try:
            with st.spinner("Analyzing your argument..."):
                response = requests.post(f"{BACKEND_URL}/evaluate-argument", json={
                    "topic": st.session_state.topic,
                    "text": user_input.strip()
                }, timeout=30)

                result = response.json()
                st.session_state.rationality_score = result.get("rationality_score")
                st.session_state.reason_for_score = result.get("reason_for_score", "")
                st.session_state.feedback = result.get("feedback", "")

            save_response = requests.post(f"{BACKEND_URL}/save-argument", json={
                "email": st.session_state.get("user_email", ""),
                "topic": st.session_state.topic,
                "argument": user_input.strip(),
                "score": st.session_state.rationality_score,
                "feedback": st.session_state.feedback
            })

            if save_response.status_code == 201:
                st.success("✅ Argument saved!")
            else:
                st.warning("⚠️ Could not save your argument.")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Evaluation failed: {str(e)}")
        except ValueError:
            st.error("❌ Invalid response from server.")

# 📊 Display results
if st.session_state.rationality_score is not None:
    st.markdown("#### 📊 Rationality Score")
    st.metric("Score", f"{st.session_state.rationality_score:.2f} / 1.00")
    st.progress(st.session_state.rationality_score)

    st.markdown("#### ✅ Strengths")
    st.write(st.session_state.reason_for_score)

    st.markdown("#### 🔎 Areas to Improve")
    st.write(st.session_state.feedback)
