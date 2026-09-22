import streamlit as st
from groq import Groq
import os
from prompts import get_study_prompt
from db import (
    init_db, save_data, get_history, clear_history,
    create_user, login_user
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PyPDF2 import PdfReader

# ================= ENV =================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ================= INIT DB =================
init_db()

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# ================= 🔁 AUTO LOGIN =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if not st.session_state.logged_in:
    if os.path.exists("session.txt"):
        with open("session.txt", "r") as f:
            saved_user = f.read()
        st.session_state.logged_in = True
        st.session_state.user = saved_user

# ================= 🔐 LOGIN / SIGNUP =================
menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

if not st.session_state.logged_in:

    if menu == "Login":
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")

        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = username

                if remember:
                    with open("session.txt", "w") as f:
                        f.write(username)

                st.success(f"Welcome {username}")
                st.rerun()
            else:
                st.error("Invalid credentials")

    elif menu == "Signup":
        st.subheader("📝 Signup")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Signup"):
            if create_user(new_user, new_pass):
                st.success("Account created successfully")
            else:
                st.error("Username already exists")

    st.stop()

# ================= 🚪 LOGOUT =================
st.sidebar.write(f"👤 {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = ""

    if os.path.exists("session.txt"):
        os.remove("session.txt")

    st.rerun()

# ================= 🌙 DARK MODE =================
dark_mode = st.toggle("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        .stApp {background-color:#0e1117; color:white;}
        </style>
    """, unsafe_allow_html=True)

st.title("📚 AI Study Assistant")

# ================= 🧠 CHAT MEMORY =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 🎯 MODE + SUBJECT =================
mode = st.selectbox("Study Mode", ["Normal", "Beginner", "Exam Revision"])
subject = st.selectbox("Subject", ["General", "Math", "Science", "Programming"])

# ================= 💬 TEXT INPUT =================
text_input = st.chat_input("Ask your question...")

user_input = text_input.strip() if text_input else None

# ================= 📄 PDF UPLOAD =================
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

if uploaded_file:
    pdf_text = extract_text(uploaded_file)

    with st.spinner("Summarizing..."):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Summarize:\n{pdf_text[:4000]}"}]
        )

    summary = response.choices[0].message.content
    st.subheader("📄 PDF Summary")
    st.success(summary)

# ================= 📜 CHAT DISPLAY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= 📥 PDF EXPORT =================
def create_pdf(text):
    doc = SimpleDocTemplate("notes.pdf")
    styles = getSampleStyleSheet()
    content = [Paragraph(text, styles["Normal"])]
    doc.build(content)

# ================= 🤖 AI =================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    prompt = get_study_prompt(user_input, mode, subject)

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

    output = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.write(output)

    st.session_state.messages.append({"role": "assistant", "content": output})

    save_data(user_input, output)

    create_pdf(output)

    with open("notes.pdf", "rb") as f:
        st.download_button("📥 Download Notes", f, file_name="notes.pdf")

# ================= 📚 HISTORY =================
st.subheader("📜 History")

history = get_history()

for row in history:
    st.write("Q:", row[1])
    st.write("A:", row[2])
    st.markdown("---")

# ================= 🧹 CLEAR =================
if st.button("🧹 Clear History"):
    clear_history()
    st.success("History cleared")
