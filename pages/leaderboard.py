import streamlit as st
import requests

# ✅ Backend URL
BACKEND_URL = "http://127.0.0.1:5000"

# ✅ Page Config
st.set_page_config(page_title="🏆 Leaderboard", layout="wide")

st.title("🏆 AI Debate Coach Leaderboard")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/profile.py")

# ✅ Logout handler
if st.query_params.get("logout") == "true":
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()

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

# ✅ Fetch leaderboard data
with st.spinner("🔄 Loading leaderboard..."):
    response = requests.get(f"{BACKEND_URL}/get-leaderboard")

if response.status_code == 200:
    leaderboard = response.json().get("leaderboard", [])

    if leaderboard:
        st.table([["📧 Email", "📊 Total Arguments", "🏆 Average Score"]] +
                 [[entry["email"], entry["total_arguments"], entry["average_score"]] for entry in leaderboard])
    else:
        st.info("No leaderboard data available.")
else:
    st.error("❌ Could not fetch leaderboard data.")

# ✅ Back Button
if st.button("⬅️ Back to Home"):
    st.switch_page("main.py")

if st.session_state.get("authenticated"):
    st.markdown("</div>", unsafe_allow_html=True)

