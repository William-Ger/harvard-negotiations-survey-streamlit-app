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

def send_email(recipient_email, total_score):
    sender_email = st.secrets["EMAIL"]
    sender_password = st.secrets["PASSWORD"]
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Your Negotiation Survey Results"
    
    if total_score >= 250:
        interpretation = ("You are probably a pretty good negotiator already. Your score indicates "
                        "that you possess many of the key traits and skills associated with successful negotiators.")
    elif total_score >= 181:
        interpretation = ("You already have many of the traits which contribute to successful negotiating. "
                        "This course will help you build upon your existing strengths and develop new skills.")
    elif total_score >= 0:
        interpretation = ("You should pay particular attention to the negotiation training materials. "
                        "While you have some negotiating skills, there's significant room for improvement.")
    else:
        interpretation = ("You should focus intensively on developing your negotiation skills. Remember, "
                        "negotiating skills can be improved with practice and proper training.")
    
    body = f"""
    Thank you for completing the Negotiation Survey!
    
    Your Total Score: {total_score}
    (Score range: -298 to +341)
    
    Score Interpretation:
    {interpretation}
    
    Key Score Ranges:
    - 250-341: Excellent negotiator
    - 181-250: Good negotiator with room for improvement
    - Below 181: Focus on developing negotiation skills
    
    Remember: Negotiating skills can be improved through practice and training!
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
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
    st.set_page_config(
        page_title="Negotiations Survey",
        page_icon="📊",
        layout="centered"
    )
    
    st.markdown("""
        <style>
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Responsive layout */
        .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Content width control */
        .content-wrapper {
            width: min(90%, 800px);
            margin: 0 auto;
        }
        
        /* Radio button styling */
        .stRadio > div {
            padding: 12px;
            background-color: var(--background-color);
            border-radius: 8px;
            margin: 8px 0;
            width: 100%;
        }
        
        .stRadio > div > div {
            gap: 8px !important;
        }
        
        .stRadio > div > div > label {
            padding: 8px 16px !important;
            margin: 4px 0;
            width: 100%;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .stRadio > div {
                background-color: rgba(255, 255, 255, 0.1);
            }
            .stRadio label {
                color: white !important;
            }
            .question-text {
                color: white !important;
            }
            .results-container {
                background-color: rgba(255, 255, 255, 0.1) !important;
            }
            .results-container h1 {
                color: #3b82f6 !important;
            }
        }
        
        /* Progress indicator */
        .stProgress {
            margin: 1.5rem 0;
        }
        
        /* Question styling */
        .question-text {
            margin: 1.5rem 0 0.75rem 0;
            font-size: 1.1rem;
            line-height: 1.5;
        }
        
        /* Results styling */
        .results-container {
            padding: 2rem;
            background-color: #f8fafc;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
        }
        
        .results-container h2 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .results-container h1 {
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: bold;
            color: #2563eb;
            margin: 1.5rem 0;
        }
        
        /* Mobile optimization */
        @media (max-width: 640px) {
            .main .block-container {
                padding: 1rem;
            }
            
            .content-wrapper {
                width: 95%;
            }
            
            .stRadio > div {
                padding: 8px;
            }
            
            .question-text {
                font-size: 1rem;
            }
        }

        /* Custom width for elements */
        .element-container {
            width: 100% !important;
        }
        
        .css-1544g2n {
            padding: 0 !important;
        }
        
        .css-1y4p8pa {
            max-width: none !important;
            width: 100% !important;
        }
        
        .stMarkdown {
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    if 'page' not in st.session_state:
        st.session_state.page = 'intro'
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'email' not in st.session_state:
        st.session_state.email = ''
    if 'email_validated' not in st.session_state:
        st.session_state.email_validated = False
    
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
        
        st.markdown("---")
        
        st.markdown("### 📧 Enter Your Email to Begin")
        
        email_input = st.text_input(
            "Email address:",
            value=st.session_state.email,
            key="email_input",
            help="Please enter a valid email address to receive your results"
        )

        if email_input:
            if is_valid_email(email_input):
                st.session_state.email = email_input
                st.session_state.email_validated = True
                
                if validate_email_connection():
                    st.success("✅ Email verified successfully!")
                    if st.button("Begin Survey", key="start_survey", use_container_width=True):
                        st.session_state.page = 'survey'
                        st.rerun()
                else:
                    st.error("Unable to verify email connection. Please try again later.")
            else:
                st.error("Please enter a valid email address")
        else:
            st.info("Please enter your email address to begin the survey")
    
    elif st.session_state.page == 'survey':
        st.markdown(f"📧 Results will be sent to: **{st.session_state.email}**")
        st.markdown("---")
        
        st.title("Negotiator Survey")
        st.subheader("How Good Are You As A Negotiator?")
        
        try:
            with open('content/quiz_data.json', 'r', encoding='utf-8') as f:
                questions = json.load(f)
        except FileNotFoundError:
            st.error("Question file not found. Please ensure 'quiz_data.json' exists in the 'content' folder.")
            return
        except json.JSONDecodeError:
            st.error("Error reading questions file. Please ensure the JSON format is correct.")
            return
        except Exception as e:
            st.error(f"An error occurred while loading questions: {str(e)}")
            return
        
        progress = len(st.session_state.responses) / len(questions)
        st.progress(progress)
        st.write(f"Progress: {int(progress * 100)}% ({len(st.session_state.responses)}/26 questions answered)")
        
        for q_num in range(1, 27):
            question = questions[str(q_num)]
            st.markdown(f"""
                <div class="question-text">
                    <strong>{q_num}. {question['text']}</strong>
                </div>
            """, unsafe_allow_html=True)
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
                st.session_state.page = 'results'
                st.rerun()
        else:
            st.warning("Please answer all questions before submitting.")
    
    elif st.session_state.page == 'results':
        st.markdown(f"📧 Results will be sent to: **{st.session_state.email}**")
        st.markdown("---")
        
        st.title("Survey Results")
        
        total_score = calculate_score(st.session_state.responses)
        
        st.markdown(f"""
        <div class="results-container">
            <h2>Your Negotiation Quotient</h2>
            <h1>{total_score}</h1>
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
            if send_email(st.session_state.email, total_score):
                st.success("✅ Results have been sent to your email!")
            else:
                st.error("Failed to send results. Please contact support.")
        
        if st.button("Take Survey Again", use_container_width=True):
            st.session_state.page = 'intro'
            st.session_state.responses = {}
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()