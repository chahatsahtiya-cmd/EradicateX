import streamlit as st
import pandas as pd
import datetime
import random
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
        background-color: #E6F2FF;
        padding: 2rem;
        border-radius: 1rem;
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
    }
    .user-chat {
        background-color: #F0F7EE;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #3DAB6D;
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

# Function to display authentication UI
def show_auth_ui():
    st.markdown("""
    <div class="blue-bg">
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
    symptoms_list = list(st.session_state.symptoms.values())
    risk_score = 0
    
    # Check for key symptoms
    if "fever" in symptoms_list:
        risk_score += 2
    if "cough" in symptoms_list or "shortness of breath" in symptoms_list:
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
    user_symptoms = [v for k, v in st.session_state.symptoms.items() if k.startswith('symptom_') and v]
    
    possible_diseases = []
    for disease, info in diseases.items():
        match_count = len(set(user_symptoms) & set(info["symptoms"]))
        if match_count > 0:
            possible_diseases.append((disease, match_count, info["description"]))
    
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
                for disease, match_count, description in possible_diseases[:2]:
                    st.markdown(f"**{disease}** ({(match_count/len(diseases[disease]['symptoms']))*100:.0f}% match)")
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
            
            # Progress tracking
            st.markdown("### Daily Progress Tracking")
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
            
            # Show progress history
            if st.session_state.progress_data.get('daily_rating'):
                st.subheader("Your Progress History")
                progress_df = pd.DataFrame(st.session_state.progress_data['daily_rating'])
                st.line_chart(progress_df.set_index('date')['rating'])
    
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
        
        st.markdown("### 📊 Symptom Tracker")
        if st.session_state.progress_data.get('symptoms_track'):
            latest = st.session_state.progress_data['symptoms_track'][-1]
            st.write(f"Today's symptoms: {', '.join(latest['symptoms']) if latest['symptoms'] else 'None reported'}")
        
        st.markdown("### 💊 Medication Adherence")
        if st.session_state.progress_data.get('medication_taken'):
            adherence = sum(1 for entry in st.session_state.progress_data['medication_taken'] if entry['taken'])
            total = len(st.session_state.progress_data['medication_taken'])
            st.write(f"Adherence rate: {adherence}/{total} days ({adherence/total*100:.0f}%)")

# Main app logic
if not st.session_state.authenticated:
    show_auth_ui()
else:
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown("""
        <div class="blue-bg">
            <h3 style="color: white;">EpidemicCare AI</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"Welcome, {st.session_state.user_data.get('name', 'User')}!")
        
        menu = st.radio("Navigation", ["AI Doctor", "Treatment Plan", "Progress Tracking", "Health Resources"])
        
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    # Main content area
    if menu == "AI Doctor":
        show_ai_doctor()
    elif menu == "Treatment Plan":
        st.markdown("""
        <div class="blue-bg">
            <h2 style="color: white;">Your Treatment Plan</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.treatment_plan:
            plan = st.session_state.treatment_plan
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Medication Schedule")
                st.table(pd.DataFrame({
                    "Medication": plan["medication"],
                    "Dosage": ["As prescribed", "As needed", "As needed"][:len(plan["medication"])],
                    "Frequency": ["Twice daily", "When needed", "When needed"][:len(plan["medication"])]
                }))
                
                st.markdown("### Diet Recommendations")
                st.info(plan["diet"])
            
            with col2:
                st.markdown("### Rest Guidelines")
                st.warning(plan["rest"])
                
                st.markdown("### Monitoring Instructions")
                st.info(plan["monitoring"])
                
                st.markdown("### Follow-up Plan")
                st.success(plan["follow_up"])
        else:
            st.info("Complete the AI doctor consultation first to generate your treatment plan")
    
    elif menu == "Progress Tracking":
        st.markdown("""
        <div class="blue-bg">
            <h2 style="color: white;">Your Progress Tracking</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.progress_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Symptom Progress")
                if st.session_state.progress_data.get('daily_rating'):
                    progress_df = pd.DataFrame(st.session_state.progress_data['daily_rating'])
                    st.line_chart(progress_df.set_index('date')['rating'])
                else:
                    st.info("No progress data yet. Complete your daily check-in.")
            
            with col2:
                st.markdown("### Medication Adherence")
                if st.session_state.progress_data.get('medication_taken'):
                    adherence = [1 if entry['taken'] else 0 for entry in st.session_state.progress_data['medication_taken']]
                    dates = [entry['date'] for entry in st.session_state.progress_data['medication_taken']]
                    adherence_df = pd.DataFrame({'date': dates, 'adherence': adherence})
                    st.bar_chart(adherence_df.set_index('date'))
                else:
                    st.info("No medication data yet.")
            
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
        else:
            st.info("Complete the AI doctor consultation first to track your progress")
    
    elif menu == "Health Resources":
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

# Footer
st.markdown("---")
st.caption("""
Disclaimer: This AI doctor is for informational purposes only and not a substitute for professional medical advice. 
Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
""")
