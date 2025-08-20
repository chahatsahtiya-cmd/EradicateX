 import streamlit as st
import pandas as pd
from datetime import date, datetime, time

# ------------------ Styling ------------------
st.set_page_config(page_title="Epidemic Care AI", layout="wide")
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #e0f7fa, #e1bee7);
    }
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #4a148c;
        text-align: center;
        padding: 10px;
    }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ Session Storage ------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "chat_stage" not in st.session_state:
    st.session_state.chat_stage = 0
    st.session_state.symptoms = {}

# ------------------ AI Doctor Dialogue ------------------
questions = [
    ("Temperature", "🌡️ What is your body temperature (°C)?", "number"),
    ("SpO2", "🫁 What is your oxygen saturation (%)?", "number"),
    ("Cough", "🤧 Do you have a cough?", "bool"),
    ("Headache", "😖 Do you have headaches?", "bool"),
    ("Sore Throat", "🗣️ Do you have a sore throat?", "bool"),
    ("Exposure", "👥 Any recent exposure to sick individuals?", "bool"),
    ("Shortness of Breath", "🚨 Do you feel shortness of breath?", "bool"),
]

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
        steps = [
            "Seek emergency medical care immediately.",
            "Avoid public transport, wear a mask if moving.",
            "Monitor oxygen continuously if available."
        ]
    elif score >= 5:
        risk = "⚠️ HIGH"
        steps = [
            "Consult a doctor within 24 hours.",
            "Isolate if respiratory symptoms are present.",
            "Track temperature and oxygen saturation twice daily."
        ]
    elif score >= 3:
        risk = "🟡 MODERATE"
        steps = [
            "Home care: rest, fluids, fever control (acetaminophen).",
            "Self-isolate if cough/fever.",
            "Seek care if symptoms worsen."
        ]
    else:
        risk = "🟢 LOW"
        steps = [
            "Monitor symptoms for 48–72 hours.",
            "Hydrate, rest, and practice hygiene.",
            "Consult a clinician if symptoms persist."
        ]

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
            st.error("Email already exists. Please log in.")
        else:
            st.session_state.users[email] = {
                "name": name,
                "password": password,
                "reminder": reminder.strftime("%H:%M"),
                "checkins": [],
                "assessments": []
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
        st.subheader("💬 AI Symptom Assessment")
        if st.session_state.chat_stage < len(questions):
            key, question, qtype = questions[st.session_state.chat_stage]
            st.info(question)

            if qtype == "number":
                val = st.number_input(key, step=1.0 if key=="Temperature" else 1)
            else:
                val = st.radio(key, ["Yes","No"])

            if st.button("Next ➡️"):
                st.session_state.symptoms[key] = val if qtype=="number" else (val=="Yes")
                st.session_state.chat_stage += 1

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
