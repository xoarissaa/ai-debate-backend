import time
import sqlite3
import streamlit as st

# ✅ Page Configuration
st.set_page_config(page_title="Real Debate Timer", layout="wide")

# ✅ Authentication Check
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/profile.py")

# ✅ Logout
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

# ✅ UI
st.title("🏆 Real Debate Timer")
st.write("This is the Real Debate Timer page. You can use it in actual debates or while sparring.")

motion = st.text_input("Enter Debate Motion")

# ✅ Timer Setup
if "time_left" not in st.session_state:
    st.session_state.time_left = 180
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_paused" not in st.session_state:
    st.session_state.timer_paused = False

st.subheader("⏳ Real Debate Mode")
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

# ✅ Display
mins, secs = divmod(st.session_state.time_left, 60)
st.markdown(f"### ⏳ Time Left: {mins}:{secs:02d}")

# ✅ Countdown + Save Usage
if st.session_state.timer_running and not st.session_state.timer_paused:
    time.sleep(1)
    st.session_state.time_left -= 1

    if st.session_state.time_left <= 0:
        st.session_state.timer_running = False
        st.success("⏰ Time's up! Great job!")

        # Save usage to DB
        email = st.session_state.get("user_email", "")
        time_used = timer_duration * 60
        if email:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usage (email, real_debate_time)
                VALUES (?, ?)
                ON CONFLICT(email) DO UPDATE SET real_debate_time = real_debate_time + ?
            """, (email, time_used, time_used))
            conn.commit()
            conn.close()

        time.sleep(2)  # Let user see the message
        st.rerun()

    else:
        st.rerun()

