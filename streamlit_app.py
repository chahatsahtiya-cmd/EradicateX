import streamlit as st
import random
import time
from datetime import datetime

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
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #A23B72;
        margin-bottom: 1rem;
    }
    .doctor-message {
        background-color: #E8F4F8;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #2E86AB;
        font-size: 1.1rem;
    }
    .user-message {
        background-color: #F0F7EE;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #3DAB6D;
        font-size: 1.1rem;
    }
    .stButton button {
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #1B5E7A;
    }
    .risk-high {
        color: #E71D36;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .risk-medium {
        color: #FF9F1C;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .risk-low {
        color: #2E86AB;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .diagnosis-box {
        background-color: #F8F9FA;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #2E86AB;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">🩺 Epidemic AI Doctor</h1>', unsafe_allow_html=True)
st.markdown("### Your virtual health assistant for epidemic disease assessment")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False

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

# Main app logic
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Consultation Chat")
    
    # Display chat history
    display_chat()
    
    # If assessment is complete, show results
    if st.session_state.assessment_complete:
        risk_level, risk_score = assess_risk()
        possible_diseases = generate_diagnosis()
        
        st.markdown("### Assessment Results")
        
        if risk_level == "high":
            st.markdown(f'<p class="risk-high">Risk Level: HIGH ({risk_score}/7 points)</p>', unsafe_allow_html=True)
            st.warning("Based on your symptoms, you may be at high risk. Please consult a healthcare professional immediately.")
        elif risk_level == "medium":
            st.markdown(f'<p class="risk-medium">Risk Level: MEDIUM ({risk_score}/7 points)</p>', unsafe_allow_html=True)
            st.info("Your symptoms suggest moderate risk. Monitor your condition and consider consulting a doctor if symptoms persist.")
        else:
            st.markdown(f'<p class="risk-low">Risk Level: LOW ({risk_score}/7 points)</p>', unsafe_allow_html=True)
            st.success("Your symptoms suggest low risk. Continue to practice good hygiene and monitor your health.")
        
        if possible_diseases:
            st.markdown("### Possible Conditions")
            for disease, match_count, description in possible_diseases[:3]:  # Show top 3 matches
                st.markdown(f"**{disease}** ({(match_count/len(diseases[disease]['symptoms']))*100:.0f}% match)")
                st.caption(description)
        
        st.markdown("### Recommended Next Steps")
        if risk_level == "high":
            st.error("1. Self-isolate immediately\n2. Contact healthcare provider\n3. Monitor symptoms closely\n4. Seek emergency care if breathing difficulties develop")
        elif risk_level == "medium":
            st.warning("1. Self-isolate as a precaution\n2. Monitor symptoms daily\n3. Consult a doctor if symptoms worsen\n4. Get tested if recommended")
        else:
            st.info("1. Practice good hygiene\n2. Monitor for new symptoms\n3. Maintain social distancing\n4. Stay hydrated and rest")
        
        if st.button("Start New Assessment"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
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
    st.markdown("### ℹ️ About This Tool")
    st.info("""
    This AI doctor is designed to help with preliminary assessment of symptoms related to epidemic diseases.
    
    **Remember:** This is not a replacement for professional medical advice. Always consult a healthcare provider for accurate diagnosis.
    """)
    
    st.markdown("### 📊 Your Progress")
    progress = st.session_state.step / len(questions)
    st.progress(progress)
    st.caption(f"Question {st.session_state.step + 1} of {len(questions)}")
    
    st.markdown("### 🦠 Common Epidemic Diseases")
    for disease in diseases:
        with st.expander(disease):
            st.write(diseases[disease]["description"])
            st.caption(f"Key symptoms: {', '.join(diseases[disease]['symptoms'])}")
    
    st.markdown("### 🛡️ Prevention Tips")
    st.success("""
    - Wash hands frequently
    - Practice social distancing
    - Wear masks in crowded places
    - Get vaccinated when available
    - Avoid touching your face
    - Disinfect frequently touched surfaces
    """)

# Footer
st.markdown("---")
st.caption("""
Disclaimer: This AI doctor is for informational purposes only and not a substitute for professional medical advice, 
diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any 
questions you may have regarding a medical condition.
""")
