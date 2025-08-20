import streamlit as st
import pandas as pd
from datetime import date, time

# ------------------ Page Config ------------------
st.set_page_config(page_title="Epidemic Care AI", layout="wide")

st.markdown("""
<style>
body {background: linear-gradient(135deg, #fce4ec, #e3f2fd); font-family: "Arial", sans-serif;}
.title {font-size:40px; font-weight:bold; color:#2e003e; text-align:center; padding:15px;}
.chat-bubble-doctor {background:#673ab7; color:white; padding:12px; border-radius:15px; margin:8px; width:70%;}
.chat-bubble-user {background:#e1bee7; color:black; padding:12px; border-radius:15px; margin:8px; width:70%; margin-left:auto;}
.card {background-color:white; padding:15px; border-radius:12px; box-shadow:2px 2px 10px rgba(0,0,0,0.1); margin:10px 0;}
.button-answer {margin:5px;}
</style>
""", unsafe_allow_html=True)

# ------------------ Session Storage ------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "chat_stage" not in st.session_state:
    st.session_state.chat_stage = 0
    st.session_state.symptoms = {}
    st.session_state.chat_history = []

# ------------------ AI Doctor Questions ------------------
questions = [
    ("Temperature", "🌡️ What is your body temperature (°C)?", "number", ["36","37","38","39","40"]),
    ("SpO2", "🫁 What is your oxygen saturation (%)?", "number", ["95","96","97","98","99","100"]),
    ("Cough", "🤧 Do you have a cough?", "bool", ["Yes","No"]),
    ("Headache", "😖 Do you have headaches?", "bool", ["Yes","No"]),
    ("Sore Throat", "🗣️ Do you have a sore throat?", "bool", ["Yes","No"]),
    ("Exposure", "👥 Any recent exposure to sick individuals?", "bool", ["Yes","No"]),
    ("Shortness of Breath", "🚨 Do you feel shortness of breath?", "bool", ["Yes","No"]),
]

# ------------------ Risk Plan ------------------
def generate_plan(symptoms):
    temp = float(symptoms.get("Temperature", 0))
    spo2 = int(symptoms.get("SpO2", 100))
    severe = symptoms.get("Shortness of Breath") or spo2 < 90

    score = 0
    if temp >= 38: score += 1
    if symptoms.get("Cough"): score += 1
    if symptoms.get("Headache"): score += 1
    if symptoms.get("Sore Throat"): score += 1
    if symptoms.get("Exposure"): score += 1
    if spo2 < 94: score += 2
    if severe: score += 3

    if severe:
        risk = "🚨 EMERGENCY"
        steps = ["Seek emergency medical care immediately.", "Avoid public transport.", "Monitor oxygen continuously."]
    elif score >= 5:
        risk = "⚠️ HIGH"
        steps = ["Consult a doctor within 24 hours.", "Isolate immediately.", "Track temp & SpO2 twice daily."]
    elif score >= 3:
        risk = "🟡 MODERATE"
        steps = ["Rest, fluids, and fever control.", "Self-isolate.", "Seek care if symptoms worsen."]
    else:
        risk = "🟢 LOW"
        steps = ["Monitor for 48–72 hours.", "Hydrate and rest.", "See doctor if persists."]
    return risk, steps

# ------------------ Auth Pages ------------------
def signup_page():
    st.markdown("<div class='title'>🩺 Epidemic Care AI - Sign Up</div>", unsafe_allow_html=True)
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    reminder = st.time_input("Daily Reminder Time", value=time(9,0))

    if st.button("Create Account"):
        if email in st.session_state.users:
            st.error("Email already exists.")
        else:
            st.session_state.users[email] = {
                "name": name, "password": password,
                "reminder": reminder.strftime("%H:%M"),
                "checkins": [], "assessments": []
            }
            st.success("Account created! Please log in.")

def login_page():
    st.markdown("<div class='title'>🔐 Login</div>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        user = st.session_state.users.get(email)
        if user and user["password"] == password:
            st.session_state.current_user = email
            st.session_state.chat_stage = 0
            st.session_state.symptoms = {}
            st.session_state.chat_history = []
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials.")

# ------------------ Dashboard ------------------
def dashboard():
    user = st.session_state.users[st.session_state.current_user]
    st.sidebar.success(f"Hello, {user['name']} 👋")
    st.markdown("<div class='title'>📊 Dashboard</div>", unsafe_allow_html=True)

    menu = st.sidebar.radio("Menu", ["Talk to AI Doctor", "Daily Check-in", "Progress", "Logout"])

    if menu == "Talk to AI Doctor":
        st.subheader("💬 Talk to the AI Doctor")

        # Display chat history
        for msg, sender in st.session_state.chat_history:
            if sender == "doctor":
                st.markdown(f"<div class='chat-bubble-doctor'>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-user'>{msg}</div>", unsafe_allow_html=True)

        if st.session_state.chat_stage < len(questions):
            key, question, qtype, options = questions[st.session_state.chat_stage]
            if not st.session_state.chat_history or st.session_state.chat_history[-1][1] != "doctor":
                st.session_state.chat_history.append((question, "doctor"))

            # Interactive buttons for answers
            col1, col2, col3, col4, col5 = st.columns(5)
            cols = [col1, col2, col3, col4, col5]
            for i, opt in enumerate(options):
                if i >= len(cols): break
                if cols[i].button(opt):
                    st.session_state.chat_history.append((opt, "user"))
                    if qtype == "number":
                        st.session_state.symptoms[key] = float(opt)
                    else:
                        st.session_state.symptoms[key] = (opt.lower() in ["yes", "y", "true"])
                    st.session_state.chat_stage += 1
                    st.rerun()
        else:
            st.success("✅ Assessment complete!")
            risk, steps = generate_plan(st.session_state.symptoms)
            st.markdown(f"### Risk Level: {risk}")
            for s in steps:
                st.write("- " + s)
            user["assessments"].append({
                "date": date.today().isoformat(),
                "risk": risk,
                "steps": steps
            })
            if st.button("Start Over"):
                st.session_state.chat_stage = 0
                st.session_state.symptoms = {}
                st.session_state.chat_history = []
                st.rerun()

    elif menu == "Daily Check-in":
        st.subheader("📝 Daily Health Check-in")
        with st.form("checkin_form"):
            score = st.slider("How bad are your symptoms today?", 0, 10, 0)
            fever = st.number_input("Fever (°C)", 30.0, 45.0, step=0.1)
            spo2 = st.number_input("SpO₂ (%)", 50, 100, step=1)
            meds = st.checkbox("Took medications today")
            notes = st.text_area("Notes / Side effects")
            submitted = st.form_submit_button("Save Check-in")
            if submitted:
                user["checkins"].append({
                    "date": date.today().isoformat(),
                    "score": score,
                    "fever": fever,
                    "spo2": spo2,
                    "meds": meds,
                    "notes": notes
                })
                st.success("Check-in saved ✅")

    elif menu == "Progress":
        st.subheader("📈 Progress Tracker")
        if user["checkins"]:
            df = pd.DataFrame(user["checkins"])
            if "date" in df.columns and {"score","fever","spo2"} <= set(df.columns):
                st.line_chart(df.set_index("date")[["score","fever","spo2"]])
            st.dataframe(df)
        else:
            st.info("No check-ins yet. Log one today!")

    elif menu == "Logout":
        st.session_state.current_user = None
        st.success("Logged out.")

# ------------------ Main ------------------
def main():
    if st.session_state.current_user:
        dashboard()
    else:
        page = st.radio("Select", ["Sign Up", "Login"])
        if page == "Sign Up":
            signup_page()
        else:
            login_page()

if __name__ == "__main__":
    main()
