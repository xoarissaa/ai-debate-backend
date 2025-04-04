import streamlit as st
import json
import os
import bcrypt
import smtplib
import random
import string
from email.message import EmailMessage

st.set_page_config(page_title="User Authentication", layout="wide")

PROFILE_FILE = "user_profile.json"

# 🎨 Hide default Streamlit UI
st.markdown("""
    <style>
        #MainMenu, header, footer, section[data-testid="stSidebar"] {
            visibility: hidden;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stTextInput > div > input {
            background-color: #1e1e1e;
            color: white;
        }
        .stTextInput label {
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Logout handler
if st.query_params.get("logout") == "true":
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    st.rerun()

# ✅ Load user data
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as file:
        user_data = json.load(file)
else:
    user_data = {}

# ✅ Password Helpers
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# ✅ Email & Code
def generate_verification_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def send_verification_email(email, code):
    sender_email = "arissa2208@gmail.com"
    sender_password = "opgr osyg edkw wppn"

    msg = EmailMessage()
    msg.set_content(f"Your verification code is: {code}")
    msg["Subject"] = "Verify Your Email"
    msg["From"] = sender_email
    msg["To"] = email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email Error:", str(e))
        return False

# 🌟 Tabs: Login / Register / Forgot Password
st.title("🔐 User Authentication")
tabs = st.tabs(["🔑 Login", "📝 Register", "🔒 Forgot Password"])

# 🔑 LOGIN
with tabs[0]:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 3])
    with col1:
        login_clicked = st.button("Login")
    with col2:
        forgot_clicked = st.button("Forgot Password?")

    if login_clicked:
        if email not in user_data:
            st.error("❌ Email not registered.")
        elif not user_data[email]["verified"]:
            st.error("⚠️ Please verify your email before logging in.")
        elif verify_password(password, user_data[email]["password"]):
            st.success(f"✅ Welcome back, {user_data[email]['name']}!")
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = email
            st.switch_page("main.py")
        else:
            st.error("❌ Incorrect password.")
    if forgot_clicked:
        st.experimental_rerun()

# 📝 REGISTER
with tabs[1]:
    st.subheader("Register New Account")
    name = st.text_input("Your Name")
    email = st.text_input("Email Address")
    password = st.text_input("Create Password", type="password")
    institution = st.text_input("Institution (School, College, etc.)")
    contact = st.text_input("Contact Number")

    if st.button("Register"):
        if not name or not email or not password or not institution or not contact:
            st.error("❌ Please fill in all fields.")
        elif email in user_data:
            st.error("❌ Email already registered.")
        else:
            code = generate_verification_code()
            if send_verification_email(email, code):
                user_data[email] = {
                    "name": name,
                    "password": hash_password(password),
                    "institution": institution,
                    "contact": contact,
                    "verified": False,
                    "verification_code": code
                }
                with open(PROFILE_FILE, "w") as file:
                    json.dump(user_data, file, indent=4)
                st.success("✅ Verification code sent! Please check your email.")
            else:
                st.error("❌ Could not send verification email.")

    if email in user_data and not user_data[email]["verified"]:
        code_input = st.text_input("Enter Verification Code")
        if st.button("Verify"):
            if code_input == user_data[email]["verification_code"]:
                user_data[email]["verified"] = True
                with open(PROFILE_FILE, "w") as file:
                    json.dump(user_data, file, indent=4)
                st.success("✅ Email verified! You can now log in.")
            else:
                st.error("❌ Incorrect verification code.")

# 🔒 FORGOT PASSWORD
with tabs[2]:
    st.subheader("Reset Your Password")
    email = st.text_input("Registered Email")
    if st.button("Send Reset Code"):
        if email in user_data:
            reset_code = generate_verification_code()
            user_data[email]["reset_code"] = reset_code
            with open(PROFILE_FILE, "w") as file:
                json.dump(user_data, file, indent=4)
            if send_verification_email(email, reset_code):
                st.success("✅ Reset code sent to your email.")
            else:
                st.error("❌ Failed to send reset code.")
        else:
            st.error("❌ Email not found.")

    reset_code_input = st.text_input("Enter Reset Code")
    new_password = st.text_input("New Password", type="password")

    if st.button("Reset Password"):
        if email in user_data and user_data[email].get("reset_code") == reset_code_input:
            user_data[email]["password"] = hash_password(new_password)
            del user_data[email]["reset_code"]
            with open(PROFILE_FILE, "w") as file:
                json.dump(user_data, file, indent=4)
            st.success("✅ Password updated. You can now log in.")
        else:
            st.error("❌ Invalid reset code.")
