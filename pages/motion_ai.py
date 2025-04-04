import streamlit as st
import requests

st.set_page_config(page_title="Motion AI", layout="wide")

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


# ✅ Logout handler
if st.query_params.get("logout") == "true":
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()

# ✅ Add Back Button
if st.button("🔙 Back to Home"):
    st.switch_page("main.py")
st.title("💡 AI Motion Generator")

topic = st.text_input("Enter a debate category (e.g., Politics, Technology)")

if st.button("Generate Motion"):
    response = requests.post("http://127.0.0.1:5000/generate-motion", json={"topic": topic})
    
    if response.status_code == 200:
        motion = response.json()["motion"]
        st.success(f"Suggested Motion: {motion}")
    else:
        st.error("Error generating motion. Check backend.")

if st.session_state.get("authenticated"):
    st.markdown("</div>", unsafe_allow_html=True)
