"""
Password Authentication Module
"""
import streamlit as st
import os


def check_password():
    expected_passwords = None
    try:
        # It can be a list of passwords in secrets.toml: app_passwords = ["pass1", "pass2"]
        expected_passwords = st.secrets.get("app_passwords", None)
        if expected_passwords is None:
            # Fallback to single password secret if app_passwords isn't found
            single_pass = st.secrets.get("app_password", None)
            if single_pass:
                expected_passwords = [single_pass]
    except Exception:
        pass

    # Fallback to Environment Variable
    if expected_passwords is None:
        env_pass = os.environ.get("PEPCO_APP_PASSWORD")
        if env_pass:
            expected_passwords = [env_pass]

    if expected_passwords is None:
        st.error("App passwords not configured. Please set 'app_passwords' in secrets or PEPCO_APP_PASSWORD environment variable.")
        return False

    # Ensure it's a list or set for membership testing
    if isinstance(expected_passwords, str):
        expected_passwords = [expected_passwords]

    def _password_entered():
        entered_pass = st.session_state.get("password", "")
        if entered_pass in expected_passwords:
            st.session_state["password_correct"] = True
            try:
                del st.session_state["password"]
            except Exception:
                pass
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", None) is True:
        return True

    # Password Page Styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #1a1a3e, #24243e, #1a1a3e);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main > div { background: transparent !important; padding: 0 !important; }
    .block-container { padding: 0rem !important; max-width: 90% !important; }
    .main-header {
        background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 30px;
        margin: 1rem 1rem 0rem 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    .password-container {
        max-width: 460px;
        margin: 40px auto 8px auto;
        padding: 2.8rem 2rem 1.8rem 2rem;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        border-radius: 32px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
    }
    .lock-icon { font-size: 3rem; margin: 1rem 0; animation: bounce 2s infinite; }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .stTextInput { margin-top: -10px !important; }
    .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 30px !important;
        color: white !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        padding: 0.9rem 1.5rem !important;
        letter-spacing: 3px;
    }
    #MainMenu, header, footer {visibility: hidden;}
    .designer-name {
        color: rgba(255,255,255,0.6) !important;
        font-size: 0.85rem !important;
        margin-top: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>📊 Plate Ratio System</h1>
        <p>Intelligent Production Planning & Ratio Optimization</p>
        <p style="font-size: 0.85rem; opacity: 0.8;">AI-Powered • Fast • Accurate</p>
        <p class="designer-name">✨ Design by Ovi ✨</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="password-container">
        <h2 style="color: white; margin: 0;">Welcome Back</h2>
        <div class="lock-icon">🔐</div>
        <p style="color: rgba(255,255,255,0.7);">Enter your secure access code to continue</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.4, 1.1, 1.4])
    with col2:
        st.text_input(
            label="",
            type="password",
            key="password",
            on_change=_password_entered,
            label_visibility="collapsed",
            placeholder="••••••••"
        )
        if st.session_state.get("password_correct") is False:
            st.error("❌ Your password is incorrect. Please contact Mr. Ovi")

    return False
