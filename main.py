import streamlit as st
import json
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCORING_KEY = {
    "1": {"a": 20, "b": 15, "c": 5, "d": -10, "e": -10},
    "2": {"a": -10, "b": -5, "c": 10, "d": 10, "e": -5},
    "3": {"a": -15, "b": 15, "c": 10, "d": -15, "e": 5},
    "4": {"a": 10, "b": 5, "c": -10, "d": 10, "e": -5},
    "5": {"a": 3, "b": 6, "c": 6, "d": -3, "e": -5},
    "6": {"a": 15, "b": 10, "c": 0, "d": -10, "e": -15},
    "7": {"a": -10, "b": -5, "c": 5, "d": 10, "e": 10},
    "8": {"a": -10, "b": 5, "c": 10, "d": 13, "e": 10},
    "9": {"a": 20, "b": 15, "c": 5, "d": -10, "e": -20},
    "10": {"a": 5, "b": 15, "c": 10, "d": -5, "e": 0},
    "11": {"a": -15, "b": -10, "c": 0, "d": 10, "e": 15},
    "12": {"a": 16, "b": 12, "c": 4, "d": -5, "e": -15},
    "13": {"a": 12, "b": 6, "c": 0, "d": -2, "e": -10},
    "14": {"a": 15, "b": 10, "c": 5, "d": -5, "e": -10},
    "15": {"a": -19, "b": -5, "c": 5, "d": 15, "e": 15},
    "16": {"a": 15, "b": 10, "c": -3, "d": -10, "e": -15},
    "17": {"a": 5, "b": 10, "c": 0, "d": -3, "e": -10},
    "18": {"a": 10, "b": 8, "c": 3, "d": -3, "e": -10},
    "19": {"a": 15, "b": 10, "c": 5, "d": -5, "e": -15},
    "20": {"a": 15, "b": 10, "c": 5, "d": 0, "e": -5},
    "21": {"a": -8, "b": -3, "c": 3, "d": 8, "e": 12},
    "22": {"a": 10, "b": 8, "c": 2, "d": -3, "e": -10},
    "23": {"a": 10, "b": 8, "c": 3, "d": 0, "e": -5},
    "24": {"a": 10, "b": 10, "c": 8, "d": -8, "e": -15},
    "25": {"a": 12, "b": 8, "c": 4, "d": -5, "e": -10},
    "26": {"a": 15, "b": 10, "c": 0, "d": -10, "e": -15}
}

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_email_connection():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(st.secrets["EMAIL"], st.secrets["PASSWORD"])
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email server connection error: {str(e)}")
        return False

def send_email(recipient_email, first_name, last_name, total_score):
    sender_email = st.secrets["EMAIL"]
    sender_password = st.secrets["PASSWORD"]
    
    cc_recipients = ["wgerstung@gibson4.com"]
    # cc_recipients = ["bburchett@gibson4.com","wgerstung@gibson4.com","wpowers@gibson4.com","lshepherd@gibson4.com"]
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Cc'] = ', '.join(cc_recipients)
    msg['Subject'] = "Your Negotiation Survey Results"
    
    if total_score >= 250:
        interpretation = "You are probably a pretty good negotiator already!"
    elif total_score >= 181:
        interpretation = "You already have many of the traits which contribute to successful negotiating."
    else:
        interpretation = "You should pay particular attention to the negotiation training materials. While you have some negotiating skills, there's significant room for improvement."
    
    body = f"""Dear {first_name} {last_name},

Thank you for completing the Negotiation Survey!

Your Total Score: {total_score}
(Score range: -298 to +341)

Score Interpretation:
{interpretation}

Key Score Ranges:
- 250-341: Excellent negotiator
- 181-250: Good negotiator with room for improvement
- Below 181: Focus on developing negotiation skills

Remember: Negotiating skills can be improved through practice and training!"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        all_recipients = [recipient_email] + cc_recipients
        server.send_message(msg, sender_email, all_recipients)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def calculate_score(responses):
    total_score = 0
    for question_num, answer in responses.items():
        total_score += SCORING_KEY[question_num][answer]
    return total_score

def main():
    # Initial page config
    st.set_page_config(
        page_title="Negotiations Survey",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # CSS for fixed header and scroll behavior
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            margin-top: -80px;
        }
        .main .block-container {
            max-width: 1200px;
            padding-top: 30px;
            padding-bottom: 0;
            margin-bottom: 0;
        }
        .element-container, .stMarkdown {
            width: 100% !important;
        }
        .stRadio > div {
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 8px;
            margin: 8px 0;
        }
        @media (prefers-color-scheme: dark) {
            .stRadio > div {
                background-color: rgba(255, 255, 255, 0.1);
            }
        }
        footer {
            visibility: hidden;
        }
        .main {
            scroll-behavior: auto !important;
        }
        .stButton button {
            margin-bottom: 0;
        }
        :root {
            --background-color: #f0f2f6;
            --primary-color: #2196F3;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: rgba(255, 255, 255, 0.1);
                --primary-color: #64B5F6;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'intro'
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'email' not in st.session_state:
        st.session_state.email = ''
    if 'first_name' not in st.session_state:
        st.session_state.first_name = ''
    if 'last_name' not in st.session_state:
        st.session_state.last_name = ''
    if 'container' not in st.session_state:
        st.session_state.container = st.empty()

    # Create a container for the main content
    with st.session_state.container.container():
        if st.session_state.page == 'intro':
            st.title("🤝 Negotiations Training")
            st.header("NEGOTIATION SURVEY")
            
            st.markdown("""
            ### Purpose
            This activity is designed to help you estimate your current negotiation skills.
            
            ### Information
            The survey focuses on your negotiating personality and your propensity to negotiate.
            Many people shy away from negotiating, preferring a quiet life. This survey will help
            you understand your natural inclination towards negotiation.
            
            ### Instructions
            * The survey contains 26 questions
            * Be honest with yourself
            * Take your time to answer each question thoughtfully
            * Your score will be calculated automatically
            * Results will be emailed to you upon completion
            
            ### Time Required
            Approximately 20 minutes
            """)
            
            st.markdown("### 📧 Enter Your Information")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name:", value=st.session_state.first_name)
            with col2:
                last_name = st.text_input("Last Name:", value=st.session_state.last_name)
            
            email = st.text_input("Email address:", value=st.session_state.email)
            
            if email and first_name and last_name:
                if is_valid_email(email):
                    st.session_state.email = email
                    st.session_state.first_name = first_name
                    st.session_state.last_name = last_name
                    
                    if validate_email_connection():
                        st.success("✅ Information verified successfully!")
                        if st.button("Begin Survey", use_container_width=True):
                            st.session_state.container.empty()
                            st.session_state.page = 'survey'
                            st.rerun()
                else:
                    st.error("Please enter a valid email address")
            else:
                st.info("Please enter all required information to begin the survey")

        elif st.session_state.page == 'survey':
            st.markdown(f"""📧 Results will be sent to: **{st.session_state.first_name} {st.session_state.last_name}** 
            ({st.session_state.email})""")
            st.markdown("---")
            
            st.title("Negotiator Survey")
            st.subheader("How Good Are You As A Negotiator?")
            
            try:
                with open('content/quiz_data.json', 'r') as f:
                    questions = json.load(f)
            except FileNotFoundError:
                questions = json.loads(st.session_state.get('quiz_data', '{}'))
            
            progress = len(st.session_state.responses) / 26
            st.progress(progress)
            st.write(f"Progress: {int(progress * 100)}% ({len(st.session_state.responses)}/26 questions answered)")
            
            for q_num in range(1, 27):
                question = questions[str(q_num)]
                st.markdown(f"**{q_num}. {question['text']}**")
                options = question['options']
                response = st.radio(
                    f"Question {q_num}",
                    options.items(),
                    format_func=lambda x: x[1],
                    key=f"q{q_num}",
                    index=None,
                    label_visibility="collapsed"
                )
                if response:
                    st.session_state.responses[str(q_num)] = response[0]
            
            st.markdown("---")
            
            if len(st.session_state.responses) == 26:
                if st.button("Submit Survey", use_container_width=True):
                    st.session_state.container.empty()
                    st.session_state.page = 'results'
                    st.rerun()
            else:
                st.warning("Please answer all questions before submitting.")

        elif st.session_state.page == 'results':
            st.markdown(f"""📧 Results will be sent to: **{st.session_state.first_name} {st.session_state.last_name}** 
            ({st.session_state.email})""")
            st.markdown("---")
            
            total_score = calculate_score(st.session_state.responses)
            
            st.title("Survey Results")
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background-color: var(--background-color); border-radius: 10px; border: 1px solid var(--primary-color);">
                <h2>Your Negotiation Quotient</h2>
                <h1 style="font-size: 3.5rem; color: var(--primary-color);">{total_score}</h1>
                <p>(Score range: -298 to +341)</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Score Interpretation")
            if total_score >= 250:
                st.success("🌟 You are probably a pretty good negotiator already!")
            elif total_score >= 181:
                st.info("✨ You already have many of the traits which contribute to successful negotiating.")
            else:
                st.warning("📚 You should pay particular attention to negotiation training materials.")
            
            with st.spinner("Sending results to your email..."):
                if send_email(st.session_state.email, st.session_state.first_name, 
                            st.session_state.last_name, total_score):
                    st.success("✅ Results have been sent to your email!")
                else:
                    st.error("Failed to send results. Please contact support.")
            
            if st.button("Take Survey Again", use_container_width=True):
                st.session_state.responses = {}
                st.session_state.first_name = ''
                st.session_state.last_name = ''
                st.session_state.email = ''
                st.session_state.container.empty()
                st.session_state.page = 'intro'
                st.rerun()

if __name__ == "__main__":
    main()