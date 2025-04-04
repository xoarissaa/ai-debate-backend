import streamlit as st
import requests

# ✅ Backend URL
BACKEND_URL = "http://127.0.0.1:5000"

# ✅ Page Config
st.set_page_config(page_title="Argument History", layout="wide")

# ✅ Logout handler
if st.query_params.get("logout") == "true":
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()

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

# ✅ Get user email
user_email = st.session_state.get("user_email", "")

# ✅ Page Title
st.title("📜 Argument History")

# ✅ Fetch arguments only if the user email exists
if user_email:
    with st.spinner("🔄 Loading history..."):
        response = requests.get(f"{BACKEND_URL}/get-arguments?email={user_email}")

    if response.status_code == 200:
        arguments = response.json().get("arguments", [])

        if arguments:
            for arg in arguments:
                st.subheader(f"🎯 Topic: {arg.get('topic', 'Unknown Topic')}")
                st.write(f"📝 **Argument:** {arg.get('argument', 'No argument provided.')}")
                st.write(f"📊 **Score:** {arg.get('score', 'N/A')}")
                st.write(f"💬 **Feedback:** {arg.get('feedback', 'No feedback available.')}")
                
                # ✅ Safe Delete Button (Avoid KeyError if 'id' is missing)
                argument_id = arg.get("id")  # Get ID safely
                if argument_id:  # Only show delete button if ID exists
                    if st.button(f"🗑️ Delete", key=f"delete_{argument_id}"):
                        delete_response = requests.post(
                            f"{BACKEND_URL}/delete-argument", json={"id": argument_id}
                        )
                        if delete_response.status_code == 200:
                            st.success("✅ Argument deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete the argument.")
                else:
                    st.warning("⚠️ This argument is missing an ID and cannot be deleted.")

                st.divider()  

        else:
            st.info("ℹ️ No saved arguments yet.")
    else:
        st.error("❌ Could not fetch argument history. Please try again later.")
else:
    st.warning("⚠️ No user email found. Please log in.")

# ✅ Navigation Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔙 Back to Home"):
        st.switch_page("main.py")
with col2:
    if st.button("⬅️ Back to Evaluation"):
        st.switch_page("main.py")

if st.session_state.get("authenticated"):
    st.markdown("</div>", unsafe_allow_html=True)