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
        padding: 2rem;
        border-radius: 1rem;
        color: white;
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
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "auth"
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

# Disease database
diseases = {
    "Influenza": {
        "symptoms": ["fever", "cough", "sore throat", "body aches", "fatigue"],
        "description": "A viral infection that attacks your respiratory system."
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "shortness of breath", "loss of taste", "loss of smell", "fatigue"],
        "description": "A contagious disease caused by the SARS-CoV-2 virus."
    },
    "Dengue Fever": {
        "symptoms": ["high fever", "severe headache", "pain behind eyes", "joint pain", "rash"],
        "description": "A mosquito-borne tropical disease caused by the dengue virus."
    },
    "Common Cold": {
        "symptoms": ["runny nose", "sneezing", "congestion", "mild cough", "sore throat"],
        "description": "A viral infection of your nose and throat."
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

# Function to navigate between pages
def navigate_to(page):
    st.session_state.page = page

# Function to display authentication UI
def show_auth_ui():
    st.markdown("""
    <div class="main">
        <h1 style="text-align: center; color: white;">🩺 EpidemicCare AI</h1>
        <p style="text-align: center; color: white;">Your intelligent health assistant for epidemic diseases</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_tab, register_tab = st.tabs(["Login", "Create Account"])
    
    with auth_tab:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            if email and password:
                st.session_state.authenticated = True
                st.session_state.user_data = {"email": email}
                st.success("Login successful!")
                time.sleep(1)
                navigate_to("consultation")
                st.experimental_rerun()
            else:
                st.error("Please enter both email and password")
    
    with register_tab:
        st.subheader("Create New Account")
        new_name = st.text_input("Full Name", key="reg_name")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Create Account", key="reg_btn"):
            if new_name and new_email and new_password:
                if new_password == confirm_password:
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        "name": new_name,
                        "email": new_email
                    }
                    st.success("Account created successfully!")
                    time.sleep(1)
                    navigate_to("consultation")
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
            possible_diseases.append((disease, match_count, info["description"], match_percentage))
    
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
            "follow_up": "Teleconsultation in 24 hours, in-person if symptoms worsen"
        },
        "medium": {
            "medication": ["Paracetamol as needed", "Decongestants if required"],
            "rest": "Adequate rest, avoid strenuous activities",
            "diet": "Increased fluid intake, balanced diet",
            "monitoring": "Check temperature twice daily",
            "follow_up": "Teleconsultation in 48 hours"
        },
        "low": {
            "medication": ["Over-the-counter symptom relief as needed"],
            "rest": "Normal activities with adequate sleep",
            "diet": "Normal healthy diet with extra fluids",
            "monitoring": "Watch for new or worsening symptoms",
            "follow_up": "Consult if symptoms persist beyond 5 days"
        }
    }
    
    return plans[risk_level]

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
                for disease, match_count, description, match_percentage in possible_diseases[:2]:
                    st.markdown(f"**{disease}** ({match_percentage:.0f}% match)")
                    st.caption(description)
            
            st.markdown("### Your Treatment Plan")
            plan = st.session_state.treatment_plan
            with st.expander("View Detailed Treatment Plan"):
                st.markdown("**Medication:**")
                for med in plan["medication"]:
                    st.markdown(f"- {med}")
                
                st.markdown(f"**Rest:** {plan['rest']}")
                st.markdown(f"**Diet:** {plan['diet']}")
                st.markdown(f"**Monitoring:** {plan['monitoring']}")
                st.markdown(f"**Follow-up:** {plan['follow_up']}")
            
            if st.button("Start Tracking My Progress"):
                navigate_to("progress")
                st.experimental_rerun()
    
    with col2:
        st.markdown("### ℹ️ Health Tips")
        st.info("""
        - Wash hands frequently with soap and water
        - Practice social distancing
        - Wear masks in crowded places
        - Get vaccinated when available
        - Disinfect frequently touched surfaces
        """)
        
        st.markdown("### 🔔 Reminders")
        st.markdown("""
        <div class="reminder-card">
            <b>Medication</b><br>
            Take prescribed medication after breakfast
        </div>
        <div class="reminder-card">
            <b>Doctor Follow-up</b><br>
            Schedule teleconsultation for tomorrow
        </div>
        <div class="reminder-card">
            <b>Hydration</b><br>
            Drink at least 8 glasses of water today
        </div>
        """, unsafe_allow_html=True)

# Function to show progress tracking
def show_progress_tracking():
    st.markdown("""
    <div class="blue-bg">
        <h2 style="color: white;">Your Progress Tracking</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.treatment_plan:
        st.warning("Please complete the AI doctor consultation first to track your progress")
        if st.button("Go to Consultation"):
            navigate_to("consultation")
            st.experimental_rerun()
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Daily Check-in")
        today = datetime.date.today()
        
        if today not in [entry['date'] for entry in st.session_state.progress_data.get('daily_rating', [])]:
            st.subheader("How are you feeling today?")
            rating = st.slider("Rate your symptoms (1-10)", 1, 10, 5, key="daily_rating")
            symptoms = st.multiselect("Current symptoms", 
                                     ["Fever", "Cough", "Headache", "Fatigue", "Body aches", "Shortness of breath"])
            meds_taken = st.checkbox("I took my medication as prescribed")
            
            if st.button("Save Today's Progress"):
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
            st.markdown("### Your Progress History")
            progress_df = pd.DataFrame(st.session_state.progress_data['daily_rating'])
            st.line_chart(progress_df.set_index('date')['rating'])
    
    with col2:
        st.markdown("### Medication Adherence")
        if st.session_state.progress_data.get('medication_taken'):
            adherence = sum(1 for entry in st.session_state.progress_data['medication_taken'] if entry['taken'])
            total = len(st.session_state.progress_data['medication_taken'])
            st.markdown(f"**Adherence rate: {adherence}/{total} days ({adherence/total*100:.0f}%)**")
            
            adherence_data = [1 if entry['taken'] else 0 for entry in st.session_state.progress_data['medication_taken']]
            dates = [entry['date'] for entry in st.session_state.progress_data['medication_taken']]
            adherence_df = pd.DataFrame({'date': dates, 'adherence': adherence_data})
            st.bar_chart(adherence_df.set_index('date'))
        else:
            st.info("No medication data yet. Complete your daily check-in.")
        
        st.markdown("### Symptom History")
        if st.session_state.progress_data.get('symptoms_track'):
            symptom_history = []
            for entry in st.session_state.progress_data['symptoms_track']:
                for symptom in entry['symptoms']:
                    symptom_history.append({'date': entry['date'], 'symptom': symptom})
            
            if symptom_history:
                symptom_df = pd.DataFrame(symptom_history)
                symptom_pivot = pd.crosstab(symptom_df['date'], symptom_df['symptom'])
                st.bar_chart(symptom_pivot)
    
    if st.button("Back to Consultation"):
        navigate_to("consultation")
        st.experimental_rerun()

# Function to show treatment plan
def show_treatment_plan():
    st.markdown("""
    <div class="blue-bg">
        <h2 style="color: white;">Your Treatment Plan</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.treatment_plan:
        st.warning("Please complete the AI doctor consultation first to generate your treatment plan")
        if st.button("Go to Consultation"):
            navigate_to("consultation")
            st.experimental_rerun()
        return
    
    plan = st.session_state.treatment_plan
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Medication Schedule")
        med_data = []
        for i, med in enumerate(plan["medication"]):
            med_data.append({
                "Medication": med,
                "Dosage": "As prescribed" if i == 0 else "As needed",
                "Frequency": "Twice daily" if i == 0 else "When needed"
            })
        st.table(pd.DataFrame(med_data))
        
        st.markdown("### Diet Recommendations")
        st.info(plan["diet"])
    
    with col2:
        st.markdown("### Rest Guidelines")
        st.warning(plan["rest"])
        
        st.markdown("### Monitoring Instructions")
        st.info(plan["monitoring"])
        
        st.markdown("### Follow-up Plan")
        st.success(plan["follow_up"])
    
    if st.button("Back to Consultation"):
        navigate_to("consultation")
        st.experimental_rerun()

# Function to show health resources
def show_health_resources():
    st.markdown("""
    <div class="blue-bg">
        <h2 style="color: white;">Health Resources</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Informational Resources")
        with st.expander("Understanding Epidemic Diseases"):
            st.write("""
            Epidemic diseases spread rapidly through populations. Common examples include:
            - Influenza (Flu)
            - COVID-19
            - Dengue Fever
            - Ebola
            - Zika Virus
            
            Early detection and proper management are crucial for recovery.
            """)
        
        with st.expander("Prevention Guidelines"):
            st.write("""
            1. Practice good hand hygiene
            2. Maintain social distancing
            3. Wear masks in public spaces
            4. Get vaccinated when available
            5. Disinfect frequently touched surfaces
            6. Avoid touching your face
            7. Stay home when feeling unwell
            """)
    
    with col2:
        st.markdown("### Emergency Contacts")
        st.markdown("""
        <div class="card">
            <h4>Local Health Department</h4>
            <p>Phone: 1-800-HELP-NOW</p>
        </div>
        <div class="card">
            <h4>Emergency Services</h4>
            <p>Phone: 911 (or local emergency number)</p>
        </div>
        <div class="card">
            <h4>24/7 Nurse Line</h4>
            <p>Phone: 1-800-NURSE-4U</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### When to Seek Emergency Care")
        st.warning("""
        Seek immediate medical attention if you experience:
        - Difficulty breathing
        - Persistent chest pain
        - Confusion or inability to stay awake
        - Bluish lips or face
        - Severe dehydration symptoms
        """)
    
    if st.button("Back to Main Menu"):
        navigate_to("main")
        st.experimental_rerun()

# Function to show main menu
def show_main_menu():
    st.markdown("""
    <div class="main">
        <h1 style="text-align: center; color: white;">🩺 EpidemicCare AI</h1>
        <p style="text-align: center; color: white;">Your intelligent health assistant for epidemic diseases</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### Welcome back, {st.session_state.user_data.get('name', 'User')}!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" onclick="alert('Navigate to consultation')">
            <h3>🩺 AI Doctor</h3>
            <p>Consult with our AI doctor for symptom assessment</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Consultation", key="consult_btn"):
            navigate_to("consultation")
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Treatment Plan</h3>
            <p>View your personalized treatment plan</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Plan", key="plan_btn"):
            navigate_to("treatment")
            st.experimental_rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Progress Tracking</h3>
            <p>Track your symptoms and recovery progress</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Track Progress", key="progress_btn"):
            navigate_to("progress")
            st.experimental_rerun()
    
    st.markdown("---")
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("### 🔔 Today's Reminders")
        st.markdown("""
        <div class="reminder-card">
            <b>Medication</b><br>
            Take prescribed medication after breakfast
        </div>
        <div class="reminder-card">
            <b>Hydration</b><br>
            Drink at least 8 glasses of water today
        </div>
        <div class="reminder-card">
            <b>Symptom Check</b><br>
            Record your symptoms and rating
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("### 📚 Health Resources")
        if st.button("View Health Resources"):
            navigate_to("resources")
            st.experimental_rerun()
        
        st.markdown("""
        <div class="card">
            <h4>Prevention Guidelines</h4>
            <p>Learn how to protect yourself and others</p>
        </div>
        <div class="card">
            <h4>Emergency Information</h4>
            <p>Important contacts and when to seek help</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("Logout", key="logout_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Main app logic
if not st.session_state.authenticated:
    show_auth_ui()
else:
    # Navigation sidebar
    with st.sidebar:
        st.markdown("""
        <div class="blue-bg">
            <h3 style="color: white;">EpidemicCare AI</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"Welcome, {st.session_state.user_data.get('name', 'User')}!")
        
        if st.button("🏠 Main Menu"):
            navigate_to("main")
        if st.button("🩺 AI Doctor"):
            navigate_to("consultation")
        if st.button("📋 Treatment Plan"):
            navigate_to("treatment")
        if st.button("📊 Progress Tracking"):
            navigate_to("progress")
        if st.button("📚 Resources"):
            navigate_to("resources")
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    # Page content
    if st.session_state.page == "main":
        show_main_menu()
    elif st.session_state.page == "consultation":
        show_ai_doctor()
    elif st.session_state.page == "treatment":
        show_treatment_plan()
    elif st.session_state.page == "progress":
        show_progress_tracking()
    elif st.session_state.page == "resources":
        show_health_resources()

# Footer
st.markdown("---")
st.caption("""
Disclaimer: This AI doctor is for informational purposes only and not a substitute for professional medical advice. 
Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
""")
