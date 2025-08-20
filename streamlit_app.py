import streamlit as st
import pandas as pd
from datetime import date, datetime

# ------------------ In-memory user storage (for demo) ------------------
if "users" not in st.session_state:
    st.session_state.users = {}  # email -> {name, password, reminder, checkins, assessments}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ------------------ Helper: Rule-based AI plan ------------------
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
            "Home care: rest, fluids, fever control (e.g., acetaminophen).",
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
    st.title("🩺 Epidemic Care - Sign Up")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    reminder = st.time_input("Daily Reminder Time", value=datetime.strptime("09:00","%H:%M").time())

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
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        user = st.session_state.users.get(email)
        if user and user["password"] == password:
            st.session_state.current_user = email
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials.")

# ------------------ App Features ------------------
def dashboard():
    user = st.session_state.users[st.session_state.current_user]
    st.sidebar.success(f"Hello, {user['name']} 👋")
    st.title("📊 Dashboard")

    menu = st.sidebar.radio("Menu", ["Assessment", "Daily Check-in", "Progress", "Logout"])

    if menu == "Assessment":
        st.subheader("Symptom Assessment")
        with st.form("assessment_form"):
            temp = st.number_input("Temperature (°C)", 30.0, 45.0, step=0.1)
            spo2 = st.number_input("Oxygen Saturation (%)", 50, 100, step=1)
            cough = st.checkbox("Cough")
            headache = st.checkbox("Headache")
            sore_throat = st.checkbox("Sore Throat")
            exposure = st.checkbox("Recent exposure to case?")
            sob = st.checkbox("Shortness of Breath")

            submitted = st.form_submit_button("Generate Plan")
            if submitted:
                symptoms = {
                    "Temperature": temp,
                    "SpO2": spo2,
                    "Cough": cough,
                    "Headache": headache,
                    "Sore Throat": sore_throat,
                    "Exposure": exposure,
                    "Shortness of Breath": sob
                }
                risk, steps = generate_plan(symptoms)
                st.success(f"**Risk Level: {risk}**")
                st.write("### Recommended Steps:")
                for s in steps:
                    st.write("- " + s)

                user["assessments"].append({
                    "date": date.today().isoformat(),
                    "risk": risk,
                    "steps": steps
                })

    elif menu == "Daily Check-in":
        st.subheader("Daily Health Check-in")
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
