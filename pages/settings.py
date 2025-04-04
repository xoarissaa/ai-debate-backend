import streamlit as st
import sqlite3
import bcrypt
 
st.title("⚙️ Settings")

email = st.session_state.get("user_email", "")

if not email:
    st.warning("⚠️ You need to log in first!")
    st.stop()

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

# ✅ Change Password
st.subheader("🔑 Change Password")
old_password = st.text_input("Current Password", type="password")
new_password = st.text_input("New Password", type="password")

if st.button("Update Password"):
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email=?", (email,))
    stored_hashed_password = cursor.fetchone()[0]

    if bcrypt.checkpw(old_password.encode(), stored_hashed_password.encode()):
        new_hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("UPDATE users SET password=? WHERE email=?", (new_hashed_password, email))
        conn.commit()
        conn.close()
        st.success("✅ Password updated successfully!")
    else:
        st.error("❌ Incorrect current password.")

# ✅ Logout Button
if st.button("🚪 Logout"):
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()

if st.session_state.get("authenticated"):
    st.markdown("</div>", unsafe_allow_html=True)