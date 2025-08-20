import streamlit as st
import pandas as pd
import datetime
import time

# Page configuration
st.set_page_config(
    page_title="EpidemicCare AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0074D9 0%, #2E86AB 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
    }
    .blue-bg {
        background-color: #0074D9;
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1.5rem;
    }
    .doctor-chat {
        background-color: #E8F4F8;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #2E86AB;
        font-size: 1.1rem;
    }
    .user-chat {
        background-color: #F0F7EE;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #3DAB6D;
        font-size: 1.1rem;
    }
    .stButton>button {
        background-color: #0074D9;
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #005BB7;
        color: white;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    .progress-bar {
        height: 1.5rem;
        background-color: #E0E0E0;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .progress-fill {
        height: 100%;
        background-color: #0074D9;
        border-radius: 10px;
        text-align: center;
        color: white;
        line-height: 1.5rem;
    }
    .reminder-card {
        background-color: #FFF4E5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FFA500;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        text-align: center;
        transition: transform 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .symptom-item {
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        background-color: #F0F8FF;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'treatment_plan' not in st.session_state:
    st.session_state.treatment_plan = {}
if 'progress_data' not in st.session_state:
    st.session_state.progress_data = {}
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

# Disease database
diseases = {
    "Influenza": {
        "symptoms": ["fever", "cough", "sore throat", "body aches", "fatigue"],
        "description": "A viral infection that attacks your respiratory system.",
        "precautions": ["Rest", "Hydration", "Over-the-counter fever reducers"]
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "shortness of breath", "loss of taste", "loss of smell", "fatigue"],
        "description": "A contagious disease caused by the SARS-CoV-2 virus.",
        "precautions": ["Isolation", "Rest", "Medical consultation", "Symptom monitoring"]
    },
    "Dengue Fever": {
        "symptoms": ["high fever", "severe headache", "pain behind eyes", "joint pain", "rash"],
        "description": "A mosquito-borne tropical disease caused by the dengue virus.",
        "precautions": ["Hydration", "Rest", "Medical supervision", "Mosquito protection"]
    },
    "Common Cold": {
        "symptoms": ["runny nose", "sneezing", "congestion", "mild cough", "sore throat"],
        "description": "A viral infection of your nose and throat.",
        "precautions": ["Rest", "Hydration", "Over-the-counter cold medicine"]
    }
}

# Doctor questions
questions = [
    "Hello! I'm Dr. AI, your medical assistant. What's your name?",
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

# Function to display welcome page
def show_welcome():
    st.markdown("""
    <div class="main">
        <h1 style="text-align: center; color: white; font-size: 3.5rem;">🩺 EpidemicCare AI</h1>
        <p style="text-align: center; color: white; font-size: 1.5rem;">Your intelligent health assistant for epidemic diseases</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <h2 style="color: #0074D9;">Welcome to EpidemicCare AI</h2>
            <p>Your personal AI doctor for epidemic disease assessment and management</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.image("https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80", 
                 use_column_width=True, caption="AI-Powered Healthcare")
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3>How it works:</h3>
            <p>1. Sign up for an account</p>
            <p>2. Consult with our AI doctor</p>
            <p>3. Receive a personalized treatment plan</p>
            <p>4. Track your daily progress</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Started", key="welcome_btn", use_container_width=True):
            st.session_state.show_welcome = False
            st.experimental_rerun()

# Function to display authentication UI
def show_auth_ui():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="blue-bg">
            <h2 style="text-align: center; color: white;">Create Account or Sign In</h2>
        </div>
        """, unsafe_allow_html=True)
        
        auth_tab, register_tab = st.tabs(["Login", "Create Account"])
        
        with auth_tab:
            st.subheader("Login to Your Account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_btn", use_container_width=True):
                if email and password:
                    st.session_state.authenticated = True
                    st.session_state.user_data = {"email": email}
                    st.success("Login successful!")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error("Please enter both email and password")
        
        with register_tab:
            st.subheader("Create New Account")
            new_name = st.text_input("Full Name", key="reg_name")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            if st.button("Create Account", key="reg_btn", use_container_width=True):
                if new_name and new_email and new_password:
                    if new_password == confirm_password:
                        st.session_state.authenticated = True
                        st.session_state.user_data = {
                            "name": new_name,
                            "email": new_email
                        }
                        st.success("Account created successfully!")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill all fields")

# Function to display chat message
def display_chat():
    for sender, message in st.session_state.chat_history:
        if sender == "doctor":
            st.markdown(f'<div class="doctor-chat"><b>Dr. AI:</b> {message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-chat"><b>You:</b> {message}</div>', unsafe_allow_html=True)

# Function to assess risk
def assess_risk():
    symptoms_list = []
    for key, value in st.session_state.symptoms.items():
        if key.startswith('symptom_') and value in ["Yes", True]:
            symptom_name = key.replace('symptom_', '').replace('_', ' ')
            symptoms_list.append(symptom_name)
    
    risk_score = 0
    
    # Check for key symptoms
    if "fever" in symptoms_list:
        risk_score += 2
    if "cough" in symptoms_list or "difficulty breathing" in symptoms_list:
        risk_score += 2
    if "loss of taste" in symptoms_list or "loss of smell" in symptoms_list:
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
    for key, value in st.session_state.symptoms.items():
        if key.startswith('symptom_') and value in ["Yes", True]:
            symptom_name = key.replace('symptom_', '').replace('_', ' ')
            user_symptoms.append(symptom_name)
    
    possible_diseases = []
    for disease, info in diseases.items():
        match_count = 0
        for symptom in user_symptoms:
            if symptom in info["symptoms"]:
                match_count += 1
        
        if match_count > 0:
            match_percentage = (match_count / len(info["symptoms"])) * 100
            possible_diseases.append((disease, match_count, info["description"], match_percentage, info["precautions"]))
    
    # Sort by match count (descending)
    possible_diseases.sort(key=lambda x: x[1], reverse=True)
    
    return possible_diseases

# Function to generate treatment plan
def generate_treatment_plan(risk_level):
    plans = {
        "high": {
            "medication": ["Antiviral medication", "Paracetamol for fever", "Cough syrup"],
            "rest": "Complete bed rest for at least 5 days",
            "diet": "Plenty of fluids, light meals, vitamin C rich foods",
            "monitoring": "Check temperature every 4 hours, monitor oxygen levels",
            "follow_up": "Teleconsultation in 24 hours, in-person if symptoms worsen",
            "duration": "7-10 days"
        },
        "medium": {
            "medication": ["Paracetamol as needed", "Decongestants if required"],
            "rest": "Adequate rest, avoid strenuous activities",
            "diet": "Increased fluid intake, balanced diet",
            "monitoring": "Check temperature twice daily",
            "follow_up": "Teleconsultation in 48 hours",
            "duration": "5-7 days"
        },
        "low": {
            "medication": ["Over-the-counter symptom relief as needed"],
            "rest": "Normal activities with adequate sleep",
            "diet": "Normal healthy diet with extra fluids",
            "monitoring": "Watch for new or worsening symptoms",
            "follow_up": "Consult if symptoms persist beyond 5 days",
            "duration": "3-5 days"
        }
    }
    
    return plans[risk_level]

# Function to show epidemic diseases info
def show_diseases_info():
    st.markdown("""
    <div class="blue-bg">
        <h3 style="color: white;">🦠 Common Epidemic Diseases</h3>
    </div>
    """, unsafe_allow_html=True)
    
    for disease, info in diseases.items():
        with st.expander(f"{disease}"):
            st.write(info["description"])
            st.markdown("**Common Symptoms:**")
            for symptom in info["symptoms"]:
                st.markdown(f'<div class="symptom-item">• {symptom.title()}</div>', unsafe_allow_html=True)
            
            st.markdown("**Precautions:**")
            for precaution in info["precautions"]:
                st.markdown(f'• {precaution}')

# Function to show precautions
def show_precautions():
    st.markdown("""
    <div class="blue-bg">
        <h3 style="color: white;">🛡️ Prevention Guidelines</h3>
    </div>
    """, unsafe_allow_html=True)
    
    precautions = [
        "Wash hands frequently with soap and water for at least 20 seconds",
        "Use alcohol-based hand sanitizer when soap is not available",
        "Avoid touching your face, especially eyes, nose, and mouth",
        "Practice social distancing (at least 6 feet from others)",
        "Wear a mask in public settings",
        "Cover your mouth and nose with a tissue when coughing or sneezing",
        "Clean and disinfect frequently touched objects and surfaces",
        "Stay home when you are sick",
        "Get vaccinated when available",
        "Maintain a healthy lifestyle with proper nutrition and exercise"
    ]
    
    for i, precaution in enumerate(precautions, 1):
        st.markdown(f"{i}. {precautions[i-1]}")

# Function to show progress tracking
def show_progress_tracking():
    st.markdown("""
    <div class="blue-bg">
        <h3 style="color: white;">📊 Your Health Progress</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.progress_data:
        st.info("Complete your consultation to start tracking progress")
        return
    
    today = datetime.date.today()
    
    if today not in [entry['date'] for entry in st.session_state.progress_data.get('daily_rating', [])]:
        st.subheader("How are you feeling today?")
        rating = st.slider("Rate your symptoms (1-10)", 1, 10, 5, key="daily_rating")
        symptoms = st.multiselect("Current symptoms", 
                                 ["Fever", "Cough", "Headache", "Fatigue", "Body aches", "Shortness of breath"])
        meds_taken = st.checkbox("I took my medication as prescribed")
        
        if st.button("Save Today's Progress", key="save_progress"):
            if 'daily_rating' not in st.session_state.progress_data:
                st.session_state.progress_data['daily_rating'] = []
            
            st.session_state.progress_data['daily_rating'].append({
                'date': today,
                'rating': rating
            })
            
            st.session_state.progress_data['symptoms_track'].append({
                'date': today,
                'symptoms': symptoms
            })
            
            st.session_state.progress_data['medication_taken'].append({
                'date': today,
                'taken': meds_taken
            })
            
            st.success("Progress saved!")
            time.sleep(1)
            st.experimental_rerun()
    else:
        st.success("You've already completed today's check-in!")
    
    # Show progress history
    if st.session_state.progress_data.get('daily_rating'):
        st.markdown("**Your Progress History**")
        progress_df = pd.DataFrame(st.session_state.progress_data['daily_rating'])
        st.line_chart(progress_df.set_index('date')['rating'])
    
    # Medication adherence
    if st.session_state.progress_data.get('medication_taken'):
        adherence = sum(1 for entry in st.session_state.progress_data['medication_taken'] if entry['taken'])
        total = len(st.session_state.progress_data['medication_taken'])
        st.markdown(f"**Medication Adherence: {adherence}/{total} days ({adherence/total*100:.0f}%)**")

# Function to show reminders
def show_reminders():
    st.markdown("""
    <div class="blue-bg">
        <h3 style="color: white;">🔔 Your Reminders</h3>
    </div>
    """, unsafe_allow_html=True)
    
    reminders = [
        {"time": "08:00 AM", "task": "Take morning medication", "completed": False},
        {"time": "12:00 PM", "task": "Drink plenty of water", "completed": False},
        {"time": "02:00 PM", "task": "Check temperature", "completed": False},
        {"time": "06:00 PM", "task": "Take evening medication", "completed": False},
        {"time": "08:00 PM", "task": "Record symptoms", "completed": False}
    ]
    
    for reminder in reminders:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write(f"**{reminder['time']}**")
        with col2:
            st.write(reminder['task'])
        with col3:
            if st.checkbox("Done", key=f"reminder_{reminder['time']}"):
                reminder['completed'] = True

# Function to show AI doctor interface
def show_ai_doctor():
    st.markdown("""
    <div class="blue-bg">
        <h2 style="color: white;">🩺 AI Doctor Consultation</h2>
        <p style="color: white;">I'm here to help assess your symptoms and provide guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Consultation Chat")
        display_chat()
        
        if st.session_state.current_step < len(questions):
            current_question = questions[st.session_state.current_step]
            
            if not st.session_state.chat_history or st.session_state.chat_history[-1][1] != current_question:
                st.session_state.chat_history.append(("doctor", current_question))
            
            if st.session_state.current_step == 0:
                name = st.text_input("Your answer:", key="input_0", label_visibility="collapsed")
                if st.button("Submit", key="button_0"):
                    if name:
                        st.session_state.symptoms['name'] = name
                        st.session_state.chat_history.append(("user", name))
                        st.session_state.current_step += 1
                        st.experimental_rerun()
            
            elif st.session_state.current_step == 1:
                age = st.number_input("Your answer:", min_value=0, max_value=120, key="input_1", label_visibility="collapsed")
                if st.button("Submit", key="button_1"):
                    st.session_state.symptoms['age'] = age
                    st.session_state.chat_history.append(("user", str(age)))
                    st.session_state.current_step += 1
                    st.experimental_rerun()
            
            elif st.session_state.current_step == 2:
                conditions = st.text_input("Your answer:", key="input_2", label_visibility="collapsed")
                if st.button("Submit", key="button_2"):
                    st.session_state.symptoms['conditions'] = conditions
                    st.session_state.chat_history.append(("user", conditions if conditions else "None"))
                    st.session_state.current_step += 1
                    st.experimental_rerun()
            
            else:
                options = ["Yes", "No", "Not sure"]
                response = st.radio("Your answer:", options, key=f"input_{st.session_state.current_step}", label_visibility="collapsed")
                if st.button("Submit", key=f"button_{st.session_state.current_step}"):
                    st.session_state.symptoms[f'symptom_{st.session_state.current_step}'] = response
                    st.session_state.chat_history.append(("user", response))
                    
                    if st.session_state.current_step == len(questions) - 1:
                        # Generate assessment
                        risk_level, risk_score = assess_risk()
                        possible_diseases = generate_diagnosis()
                        st.session_state.treatment_plan = generate_treatment_plan(risk_level)
                        
                        # Initialize progress tracking
                        st.session_state.progress_data = {
                            "start_date": datetime.date.today(),
                            "symptoms_track": [],
                            "medication_taken": [],
                            "daily_rating": []
                        }
                    else:
                        st.session_state.current_step += 1
                    
                    st.experimental_rerun()
        
        else:
            # Show assessment results
            risk_level, risk_score = assess_risk()
            possible_diseases = generate_diagnosis()
            
            st.markdown("### Assessment Results")
            
            if risk_level == "high":
                st.error(f"Risk Level: HIGH ({risk_score}/7 points)")
                st.warning("Based on your symptoms, you may be at high risk. Please consult a healthcare professional immediately.")
            elif risk_level == "medium":
                st.warning(f"Risk Level: MEDIUM ({risk_score}/7 points)")
                st.info("Your symptoms suggest moderate risk. Monitor your condition and consider consulting a doctor if symptoms persist.")
            else:
                st.success(f"Risk Level: LOW ({risk_score}/7 points)")
                st.info("Your symptoms suggest low risk. Continue to practice good hygiene and monitor your health.")
            
            if possible_diseases:
                st.markdown("### Possible Conditions")
                for disease, match_count, description, match_percentage, precautions in possible_diseases[:2]:
                    st.markdown(f"**{disease}** ({match_percentage:.0f}% match)")
                    st.caption(description)
            
            st.markdown("### Your Treatment Plan")
            plan = st.session_state.treatment_plan
            
            st.markdown("**Medication:**")
            for med in plan["medication"]:
                st.markdown(f"- {med}")
            
            st.markdown(f"**Rest:** {plan['rest']}")
            st.markdown(f"**Diet:** {plan['diet']}")
            st.markdown(f"**Monitoring:** {plan['monitoring']}")
            st.markdown(f"**Follow-up:** {plan['follow_up']}")
            st.markdown(f"**Expected Duration:** {plan['duration']}")
            
            if st.button("Start Tracking My Progress"):
                st.session_state.progress_data = {
                    "start_date": datetime.date.today(),
                    "symptoms_track": [],
                    "medication_taken": [],
                    "daily_rating": []
                }
                st.experimental_rerun()
    
    with col2:
        # Disease information
        show_diseases_info()
        
        # Precautions
        show_precautions()
        
        # Progress tracking
        show_progress_tracking()
        
        # Reminders
        show_reminders()

# Main app logic
if st.session_state.show_welcome:
    show_welcome()
elif not st.session_state.authenticated:
    show_auth_ui()
else:
    # Header with user info and logout
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown(f"### Welcome, {st.session_state.user_data.get('name', 'User')}!")
    
    with col3:
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    # Main content
    show_ai_doctor()

# Footer with disclaimer
st.markdown("---")
st.markdown("""
<div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem;">
    <h4>⚠️ Disclaimer</h4>
    <p><strong>This application is for prototype and educational purposes only.</strong></p>
    <p>It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any 
    questions you may have regarding a medical condition. Never disregard professional 
    medical advice or delay in seeking it because of something you have read in this application.</p>
    <p>If you think you may have a medical emergency, call your doctor or emergency services immediately.</p>
</div>
""", unsafe_allow_html=True)
