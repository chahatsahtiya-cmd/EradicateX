import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# Page configuration
st.set_page_config(
    page_title="Epidemic AI Doctor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main background styling */
    .stApp {
        background: linear-gradient(135deg, #e0f7fa 0%, #bbdefb 100%);
    }
    
    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        color: #0066cc;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        font-weight: 700;
    }
    
    /* Card styling */
    .card {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-left: 5px solid #0066cc;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(to right, #0066cc, #0099ff);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton button:hover {
        background: linear-gradient(to right, #0055aa, #0088ee);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Doctor message styling */
    .doctor-message {
        background-color: rgba(224, 247, 250, 0.8);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #0066cc;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* User message styling */
    .user-message {
        background-color: rgba(187, 222, 251, 0.8);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #0066cc;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Risk level styling */
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.5rem;
    }
    
    .risk-medium {
        color: #ffa64b;
        font-weight: bold;
        font-size: 1.5rem;
    }
    
    .risk-low {
        color: #00cc66;
        font-weight: bold;
        font-size: 1.5rem;
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #bbdefb;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(to right, #0066cc, #0099ff);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #e0f7fa 0%, #bbdefb 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Sign Up"
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'symptoms' not in st.session_state:
        st.session_state.symptoms = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'daily_reports' not in st.session_state:
        st.session_state.daily_reports = []
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

init_session_state()

# Disease database
diseases = {
    "Influenza": {
        "symptoms": ["fever", "cough", "sore throat", "body aches", "fatigue"],
        "description": "A viral infection that attacks your respiratory system.",
        "severity": "Moderate"
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "shortness of breath", "loss of taste", "loss of smell", "fatigue"],
        "description": "A contagious disease caused by the SARS-CoV-2 virus.",
        "severity": "High"
    },
    "Dengue Fever": {
        "symptoms": ["high fever", "severe headache", "pain behind eyes", "joint pain", "rash"],
        "description": "A mosquito-borne tropical disease caused by the dengue virus.",
        "severity": "High"
    },
    "Common Cold": {
        "symptoms": ["runny nose", "sneezing", "congestion", "mild cough", "sore throat"],
        "description": "A viral infection of your nose and throat.",
        "severity": "Low"
    }
}

# Doctor questions
questions = [
    "Hello! I'm Dr. StreamLit, your AI medical assistant. What's your name?",
    "Nice to meet you! How old are you?",
    "Do you have any pre-existing medical conditions?",
    "Let's talk about your symptoms. Have you had a fever in the last 48 hours?",
    "Are you experiencing any cough or difficulty breathing?",
    "Do you have any body aches or joint pain?",
    "Have you noticed any loss of taste or smell?",
    "Are you experiencing fatigue or unusual tiredness?",
    "Any other symptoms you'd like to mention?",
    "Thank you. I'm now analyzing your symptoms..."
]

# Function to display chat message
def display_chat():
    for sender, message in st.session_state.chat_history:
        if sender == "doctor":
            st.markdown(f'<div class="doctor-message"><b>Dr. StreamLit:</b> {message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message"><b>You:</b> {message}</div>', unsafe_allow_html=True)

# Function to assess risk
def assess_risk():
    symptoms_list = [v for k, v in st.session_state.symptoms.items() if k.startswith('symptom_') and v.lower() == 'yes']
    risk_score = 0
    
    # Check for key symptoms
    if any('fever' in s.lower() for s in symptoms_list):
        risk_score += 2
    if any('cough' in s.lower() for s in symptoms_list) or any('breathing' in s.lower() for s in symptoms_list):
        risk_score += 2
    if any('taste' in s.lower() for s in symptoms_list) or any('smell' in s.lower() for s in symptoms_list):
        risk_score += 3
    
    # Determine risk level
    if risk_score >= 5:
        return "high", risk_score
    elif risk_score >= 3:
        return "medium", risk_score
    else:
        return "low", risk_score

# Function to generate diagnosis
def generate_diagnosis():
    user_symptoms = []
    for k, v in st.session_state.symptoms.items():
        if k.startswith('symptom_') and v.lower() == 'yes':
            # Map the question to actual symptom names
            if 'fever' in k:
                user_symptoms.append('fever')
            elif 'cough' in k or 'breathing' in k:
                user_symptoms.extend(['cough', 'shortness of breath'])
            elif 'aches' in k or 'joint' in k:
                user_symptoms.append('body aches')
                user_symptoms.append('joint pain')
            elif 'taste' in k or 'smell' in k:
                user_symptoms.extend(['loss of taste', 'loss of smell'])
            elif 'fatigue' in k:
                user_symptoms.append('fatigue')
    
    possible_diseases = []
    for disease, info in diseases.items():
        match_count = len(set(user_symptoms) & set(info["symptoms"]))
        if match_count > 0:
            possible_diseases.append((disease, match_count, info["description"], info["severity"]))
    
    # Sort by match count (descending)
    possible_diseases.sort(key=lambda x: x[1], reverse=True)
    
    return possible_diseases

# Function to create a daily report
def create_daily_report():
    risk_level, risk_score = assess_risk()
    possible_diseases = generate_diagnosis()
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "risk_level": risk_level,
        "risk_score": risk_score,
        "possible_conditions": [d[0] for d in possible_diseases[:2]],
        "symptoms_reported": len([v for k, v in st.session_state.symptoms.items() if k.startswith('symptom_') and v.lower() == 'yes'])
    }
    
    st.session_state.daily_reports.append(report)
    return report

# Function to display progress charts
def display_progress_charts():
    if not st.session_state.daily_reports:
        st.info("No progress data available yet. Complete your first assessment to see your progress.")
        return
    
    dates = [r['date'] for r in st.session_state.daily_reports]
    risk_scores = [r['risk_score'] for r in st.session_state.daily_reports]
    symptoms = [r['symptoms_reported'] for r in st.session_state.daily_reports]
    
    # Create a DataFrame for the reports
    df = pd.DataFrame(st.session_state.daily_reports)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Risk Score Trend', 'Symptoms Reported', 'Risk Level Distribution', 'Condition Frequency'),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Risk score trend
    fig.add_trace(
        go.Scatter(x=dates, y=risk_scores, mode='lines+markers', name='Risk Score',
                  line=dict(color='#0066cc', width=3)),
        row=1, col=1
    )
    
    # Symptoms reported
    fig.add_trace(
        go.Bar(x=dates, y=symptoms, name='Symptoms', marker_color='#ff4b4b'),
        row=1, col=2
    )
    
    # Risk level distribution
    risk_levels = [r['risk_level'] for r in st.session_state.daily_reports]
    risk_counts = pd.Series(risk_levels).value_counts()
    fig.add_trace(
        go.Pie(labels=risk_counts.index, values=risk_counts.values, 
               marker=dict(colors=['#00cc66', '#ffa64b', '#ff4b4b'])),
        row=2, col=1
    )
    
    # Condition frequency
    all_conditions = []
    for report in st.session_state.daily_reports:
        all_conditions.extend(report['possible_conditions'])
    
    if all_conditions:
        condition_counts = pd.Series(all_conditions).value_counts()
        fig.add_trace(
            go.Bar(x=condition_counts.index, y=condition_counts.values, 
                   marker_color=['#0066cc', '#0099ff', '#00cc66', '#ffa64b']),
            row=2, col=2
        )
    
    fig.update_layout(height=600, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# Sign Up Page
def sign_up_page():
    st.markdown('<h1 class="main-header">🩺 Epidemic AI Doctor</h1>', unsafe_allow_html=True)
    st.markdown("### Create your account to get started")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            
        with col2:
            age = st.number_input("Age", min_value=1, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
            phone = st.text_input("Phone Number")
        
        medical_history = st.text_area("Medical History (optional)")
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not name or not email or not password:
                st.error("Please fill in all required fields")
            else:
                st.session_state.user_data = {
                    "name": name,
                    "email": email,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "medical_history": medical_history
                }
                st.session_state.logged_in = True
                st.session_state.current_page = "AI Doctor"
                st.success("Account created successfully! Redirecting to AI Doctor...")
                time.sleep(1)
                st.experimental_rerun()

# AI Doctor Page
def ai_doctor_page():
    st.markdown('<h1 class="main-header">🩺 Epidemic AI Doctor</h1>', unsafe_allow_html=True)
    st.markdown("### Your virtual health assistant for epidemic disease assessment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Consultation Chat")
        
        # Display chat history
        display_chat()
        
        # If assessment is complete, show results
        if st.session_state.assessment_complete:
            risk_level, risk_score = assess_risk()
            possible_diseases = generate_diagnosis()
            
            st.markdown("### Assessment Results")
            
            if risk_level == "high":
                st.markdown(f'<p class="risk-high">Risk Level: HIGH ({risk_score}/7 points)</p>', unsafe_allow_html=True)
                st.error("Based on your symptoms, you may be at high risk. Please consult a healthcare professional immediately.")
            elif risk_level == "medium":
                st.markdown(f'<p class="risk-medium">Risk Level: MEDIUM ({risk_score}/7 points)</p>', unsafe_allow_html=True)
                st.warning("Your symptoms suggest moderate risk. Monitor your condition and consider consulting a doctor if symptoms persist.")
            else:
                st.markdown(f'<p class="risk-low">Risk Level: LOW ({risk_score}/7 points)</p>', unsafe_allow_html=True)
                st.success("Your symptoms suggest low risk. Continue to practice good hygiene and monitor your health.")
            
            if possible_diseases:
                st.markdown("### Possible Conditions")
                for disease, match_count, description, severity in possible_diseases[:3]:
                    severity_color = "#ff4b4b" if severity == "High" else "#ffa64b" if severity == "Moderate" else "#00cc66"
                    st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.8); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid {severity_color}'>
                        <h4>{disease} ({(match_count/len(diseases[disease]['symptoms']))*100:.0f}% match)</h4>
                        <p>{description}</p>
                        <p><strong>Severity:</strong> <span style='color: {severity_color}'>{severity}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("### Recommended Next Steps")
            if risk_level == "high":
                st.error("""
                1. Self-isolate immediately
                2. Contact healthcare provider
                3. Monitor symptoms closely
                4. Seek emergency care if breathing difficulties develop
                """)
            elif risk_level == "medium":
                st.warning("""
                1. Self-isolate as a precaution
                2. Monitor symptoms daily
                3. Consult a doctor if symptoms worsen
                4. Get tested if recommended
                """)
            else:
                st.info("""
                1. Practice good hygiene
                2. Monitor for new symptoms
                3. Maintain social distancing
                4. Stay hydrated and rest
                """)
            
            if st.button("Save Daily Report"):
                report = create_daily_report()
                st.success(f"Daily report saved for {report['date']}")
            
            if st.button("Start New Assessment"):
                st.session_state.step = 0
                st.session_state.symptoms = {}
                st.session_state.chat_history = []
                st.session_state.assessment_complete = False
                st.experimental_rerun()
        
        # If assessment is not complete, continue questions
        elif st.session_state.step < len(questions):
            current_question = questions[st.session_state.step]
            
            # Add doctor's question to chat if not already there
            if not st.session_state.chat_history or st.session_state.chat_history[-1][1] != current_question:
                st.session_state.chat_history.append(("doctor", current_question))
            
            # Handle different types of questions
            if st.session_state.step == 0:  # Name
                name = st.text_input("Your answer:", key="input_0", label_visibility="collapsed")
                if st.button("Submit", key="button_0"):
                    if name:
                        st.session_state.symptoms['name'] = name
                        st.session_state.chat_history.append(("user", name))
                        st.session_state.step += 1
                        st.experimental_rerun()
            
            elif st.session_state.step == 1:  # Age
                age = st.number_input("Your answer:", min_value=0, max_value=120, key="input_1", label_visibility="collapsed")
                if st.button("Submit", key="button_1"):
                    st.session_state.symptoms['age'] = age
                    st.session_state.chat_history.append(("user", str(age)))
                    st.session_state.step += 1
                    st.experimental_rerun()
            
            elif st.session_state.step == 2:  # Medical conditions
                conditions = st.text_input("Your answer:", key="input_2", label_visibility="collapsed")
                if st.button("Submit", key="button_2"):
                    st.session_state.symptoms['conditions'] = conditions
                    st.session_state.chat_history.append(("user", conditions if conditions else "None"))
                    st.session_state.step += 1
                    st.experimental_rerun()
            
            else:  # Symptom questions
                options = ["Yes", "No", "Not sure"]
                response = st.radio("Your answer:", options, key=f"input_{st.session_state.step}", label_visibility="collapsed")
                if st.button("Submit", key=f"button_{st.session_state.step}"):
                    st.session_state.symptoms[f'symptom_{st.session_state.step}'] = response
                    st.session_state.chat_history.append(("user", response))
                    
                    # If this is the last question, complete assessment
                    if st.session_state.step == len(questions) - 1:
                        st.session_state.assessment_complete = True
                    else:
                        st.session_state.step += 1
                    
                    st.experimental_rerun()
    
    with col2:
        st.markdown("#### ℹ️ User Profile")
        if st.session_state.user_data:
            user = st.session_state.user_data
            st.markdown(f"""
            <div class="card">
                <h4>{user.get('name', 'User')}</h4>
                <p><strong>Age:</strong> {user.get('age', 'N/A')}</p>
                <p><strong>Gender:</strong> {user.get('gender', 'N/A')}</p>
                <p><strong>Email:</strong> {user.get('email', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### 🦠 Common Epidemic Diseases")
        for disease in diseases:
            with st.expander(disease):
                st.write(diseases[disease]["description"])
                st.caption(f"Key symptoms: {', '.join(diseases[disease]['symptoms'])}")
                severity_color = "#ff4b4b" if diseases[disease]["severity"] == "High" else "#ffa64b" if diseases[disease]["severity"] == "Moderate" else "#00cc66"
                st.caption(f"Severity: <span style='color: {severity_color}'>{diseases[disease]['severity']}</span>", unsafe_allow_html=True)
        
        st.markdown("#### 🛡️ Prevention Tips")
        st.success("""
        - Wash hands frequently
        - Practice social distancing
        - Wear masks in crowded places
        - Get vaccinated when available
        - Avoid touching your face
        - Disinfect frequently touched surfaces
        """)

# Progress Report Page
def progress_report_page():
    st.markdown('<h1 class="main-header">📊 Your Health Progress</h1>', unsafe_allow_html=True)
    
    if not st.session_state.daily_reports:
        st.info("No progress data available yet. Complete your first assessment to see your progress.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Health Trends Over Time")
        display_progress_charts()
    
    with col2:
        st.markdown("### Latest Report Summary")
        latest_report = st.session_state.daily_reports[-1]
        
        st.markdown(f"""
        <div class="card">
            <h4>Report Date: {latest_report['date']}</h4>
            <p><strong>Risk Level:</strong> <span class="risk-{latest_report['risk_level']}">{latest_report['risk_level'].upper()}</span></p>
            <p><strong>Risk Score:</strong> {latest_report['risk_score']}/7</p>
            <p><strong>Symptoms Reported:</strong> {latest_report['symptoms_reported']}</p>
            <p><strong>Possible Conditions:</strong> {', '.join(latest_report['possible_conditions']) if latest_report['possible_conditions'] else 'None identified'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Previous Reports")
        for i, report in enumerate(reversed(st.session_state.daily_reports[:-1])):
            if i < 3:  # Show only last 3 reports
                with st.expander(f"Report from {report['date']}"):
                    st.write(f"Risk Level: {report['risk_level'].upper()}")
                    st.write(f"Risk Score: {report['risk_score']}/7")
                    st.write(f"Symptoms: {report['symptoms_reported']}")
                    st.write(f"Conditions: {', '.join(report['possible_conditions']) if report['possible_conditions'] else 'None'}")

# Navigation
def main():
    # Sidebar navigation
    st.sidebar.markdown("# 🩺 Navigation")
    
    if st.session_state.logged_in:
        pages = {
            "AI Doctor": ai_doctor_page,
            "Progress Report": progress_report_page
        }
        
        selected_page = st.sidebar.radio("Go to", list(pages.keys()))
        
        if st.sidebar.button("Logout"):
            init_session_state()
            st.experimental_rerun()
        
        # Display the selected page
        pages[selected_page]()
    else:
        sign_up_page()
    
    # Footer
    st.markdown("---")
    st.caption("""
    Disclaimer: This AI doctor is for informational purposes only and not a substitute for professional medical advice, 
    diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any 
    questions you may have regarding a medical condition.
    """)

if __name__ == "__main__":
    main()
