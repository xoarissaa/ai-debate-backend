import streamlit as st
import json
import os
import sqlite3

# ✅ Setup
st.set_page_config(page_title="👤 Dashboard", layout="wide")

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

# ✅ Handle logout
if st.query_params.get("logout") == "true":
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()

# ✅ Auth check
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/profile.py")

# ✅ Load user info
email = st.session_state.get("user_email", "")
PROFILE_FILE = "user_profile.json"

# Fallback if file missing
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        user_data = json.load(f)
    profile = user_data.get(email, {})
else:
    user_data = {}
    profile = {}

# ✅ Profile Dashboard UI
st.title("👤 Your Profile Dashboard")
col1, col2 = st.columns([1, 3])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
    st.markdown(f"**👤 Name:** {profile.get('name', 'User')}")
    st.markdown(f"**📧 Email:** {email}")
    st.markdown(f"**📱 Contact:** {profile.get('contact', 'Not provided')}")
    st.markdown(f"**🏫 Institution:** {profile.get('institution', 'Not provided')}")

with col2:
    # Timer stats
    total_practice = 0
    total_real = 0

    if email:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT practice_time, real_debate_time FROM usage WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result:
            total_practice, total_real = result
        conn.close()

    total_time = total_practice + total_real
    st.metric("Practice Timer Used", f"{total_practice:.1f} seconds")
    st.metric("Real Debate Timer Used", f"{total_real:.1f} seconds")
    st.metric("Total Time Spent", f"{total_time:.1f} seconds")

# 🛠️ Collapsible Edit Profile Section
with st.expander("✏️ Edit Your Profile"):
    new_name = st.text_input("Name", value=profile.get("name", ""))
    new_contact = st.text_input("Contact Number", value=profile.get("contact", ""))
    new_institution = st.text_input("Institution", value=profile.get("institution", ""))

    if st.button("Update Profile", use_container_width=True):
        if email:
            user_data[email]["name"] = new_name
            user_data[email]["contact"] = new_contact
            user_data[email]["institution"] = new_institution

            with open(PROFILE_FILE, "w") as f:
                json.dump(user_data, f, indent=4)

        st.success("✅ Profile updated successfully!")

# 🚪 Logout
if st.button("🚪 Logout"):
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()
