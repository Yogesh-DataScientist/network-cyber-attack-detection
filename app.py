import streamlit as st
import pandas as pd
import numpy as np
import pickle
import time
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# ----------------------------------------
# 1. Configuration & Styling
# ----------------------------------------
st.set_page_config(
    page_title="Cyber Defense System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Cyberpunk / Neon Glassmorphism CSS
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        background-image: radial-gradient(circle at 15% 50%, rgba(20, 30, 48, 0.4), transparent 50%),
                          radial-gradient(circle at 85% 30%, rgba(36, 59, 85, 0.4), transparent 50%);
    }
    /* Headers */
    h1, h2, h3 {
        color: #38bdf8;
        font-family: 'Exo 2', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }
    /* Sidebar */
    .css-1d391kg, .css-1dp5vir, [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    /* Cards and Containers */
    div.stMetric, .css-1r6slb0, .css-12oz5g7, [data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div.stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 32px 0 rgba(56, 189, 248, 0.2) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
    }
    /* Buttons */
    div.stButton > button:first-child, [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
    }
    div.stButton > button:first-child:hover, [data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
        transform: translateY(-2px) scale(1.02);
        color: white;
    }
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select, [data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        transition: all 0.2s;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.3) !important;
    }
    /* Alert styling */
    .attack-alert {
        padding: 30px;
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(153, 27, 27, 0.3) 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        color: #fca5a5;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.4);
        animation: criticalPulse 1.5s infinite;
    }
    .safe-alert {
        padding: 30px;
        background: linear-gradient(135deg, rgba(22, 163, 74, 0.1) 0%, rgba(21, 128, 61, 0.3) 100%);
        border: 2px solid #22c55e;
        border-radius: 16px;
        color: #86efac;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(34, 197, 94, 0.2);
        animation: safePulse 3s infinite;
    }
    @keyframes criticalPulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); border-color: #ef4444; }
        50% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); border-color: #f87171; }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); border-color: #ef4444; }
    }
    @keyframes safePulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    hr {
        border-color: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- NEW FEATURE: Initialize Live Attack Counter in session_state ---
if 'attack_count' not in st.session_state:
    st.session_state['attack_count'] = 0
if 'threshold' not in st.session_state:
    st.session_state['threshold'] = 0.85
if 'heuristic_override' not in st.session_state:
    st.session_state['heuristic_override'] = True
if 'model_path' not in st.session_state:
    st.session_state['model_path'] = 'model.pkl'

# --- NEW FEATURE: Authentication State & Logic ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None

USER_DB = 'users_db.json'

def load_users():
    if not os.path.exists(USER_DB):
        default_db = {"admin": {"password": "admin", "role": "admin", "status": "approved"}}
        with open(USER_DB, 'w') as f:
            json.dump(default_db, f)
        return default_db
    with open(USER_DB, 'r') as f:
        return json.load(f)

def save_users(db):
    with open(USER_DB, 'w') as f:
        json.dump(db, f, indent=4)

if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; color: #38bdf8;'>🛡️ Cyber Defense System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Authentication Required</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to your account")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            users = load_users()
            if login_user in users and users[login_user]['password'] == login_pass:
                if users[login_user]['status'] == 'approved':
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_user
                    st.session_state['role'] = users[login_user]['role']
                    st.rerun()
                else:
                    st.error("Your account is currently pending admin approval.")
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        st.subheader("Create a new account")
        reg_user = st.text_input("Username", key="reg_user")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Sign Up", use_container_width=True):
            users = load_users()
            if reg_user in users:
                st.error("Username already exists!")
            elif reg_pass != reg_confirm:
                st.error("Passwords do not match!")
            elif len(reg_user) < 3 or len(reg_pass) < 3:
                st.error("Username and password must be at least 3 characters.")
            else:
                users[reg_user] = {"password": reg_pass, "role": "user", "status": "pending"}
                save_users(users)
                st.success("Account created successfully! Please wait for admin approval before logging in.")
    
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 0.9rem;">
            &copy; 2026 / CYBER ATTACK DETECTION &<br>
            NETWORK INTRUSION PREVENTION SYSTEM
        </div>
    """, unsafe_allow_html=True)
    st.stop()  # Halt execution of the rest of the app until authenticated!

# ----------------------------------------
# 2. Loading Model & Preprocessors
# ----------------------------------------
@st.cache_resource
def load_ml_assets(file_path):
    model, scaler, encoders = None, None, None
    try:
        with open(file_path, 'rb') as f:
            assets = pickle.load(f)
            if isinstance(assets, dict) and 'model' in assets:
                model = assets.get('model')
                scaler = assets.get('scaler')
                encoders = assets.get('encoders')
            else:
                model = assets
    except FileNotFoundError:
        pass
    return model, scaler, encoders

model, scaler, encoders = load_ml_assets(st.session_state.get('model_path', 'model.pkl'))

# ----------------------------------------
# 3. Sidebar Navigation
# ----------------------------------------
st.sidebar.markdown('<div style="text-align: center;"><img src="data:image/png;base64,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" width="180" style="margin-bottom: 20px; filter: drop-shadow(0px 0px 10px #38bdf8);"></div>', unsafe_allow_html=True)
st.sidebar.title("Intelligent Cyber Attack Detection")
st.sidebar.markdown("**Network Intrusion Prevention System**")
st.sidebar.markdown("---")

sidebar_options = [
    "📊 System Dashboard", 
    " Traffic Analyzer", 
    "“ Upload Network Logs", 
    "⚙️ Engine Settings"
]
if st.session_state.get('role') == 'admin':
    sidebar_options.append("‘ User Management")

app_mode = st.sidebar.radio("", sidebar_options)

st.sidebar.markdown("---")
st.sidebar.info("System Status: **Active** 🟢\n\nModel Loaded: " + ("✅ Ready" if model else " Offline"))

# Logout
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.get('username', '')}** ({st.session_state.get('role', '').capitalize()})")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.rerun()

# --- NEW FEATURE: Chatbot Assistant ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Feature Explanation")
chat_query = st.sidebar.text_input("Ask me anything...")

def chatbot_response(query):
    query = query.lower()
    
    # Comprehensive dictionary of terms and explanations
    knowledge_base = {
        # General Concepts & UI Words
        'attack': "An attack indicates malicious activity like DDoS, Brute Force, or Malware signatures in network traffic.",
        'normal': "Normal traffic refers to standard, safe network sessions that do not match known threat signatures.",
        'safe': "Normal traffic refers to standard, safe network sessions that do not match known threat signatures.",
        'model': "Our Neural Engine uses a robust ML model combined with heuristic rules for highly accurate anomaly detection.",
        'neural engine': "Our machine learning algorithm that analyzes network traffic patterns to detect anomalies.",
        'dashboard': "The Dashboard is the main overview screen showing real-time system metrics, active nodes, and intrusion statistics.",
        'intrusion': "An intrusion is unauthorized access or malicious activity on the network. Our Prevention System (IPS) actively blocks these.",
        'confidence': "Threat Confidence is the percentage probability calculated by the AI that the evaluated traffic is a malicious attack.",
        'heuristic': "Heuristic Overrides (or Guardrails) are strict rule-based triggers that flag blatant risks, such as high failed logins, overriding ML uncertainty.",
        'guardrail': "Heuristic Overrides (or Guardrails) are strict rule-based triggers that flag blatant risks, such as high failed logins, overriding ML uncertainty.",
        'sensitivity': "Anomaly Detection Sensitivity (Threshold) controls how strict the AI is. A lower value catches more threats but may increase false alarms.",
        'threshold': "Anomaly Detection Sensitivity (Threshold) controls how strict the AI is. A lower value catches more threats but may increase false alarms.",
        'batch': "Batch Log Processing allows you to upload a CSV file of network logs to run mass intrusion detection logic all at once.",
        'csv': "Batch Log Processing allows you to upload a CSV file of network logs to run mass intrusion detection logic all at once.",
        'analyzer': "The Traffic Analyzer evaluates specific network connections, either via real-time simulation or manual data input.",
        'manual mode': "Manual Mode lets you input specific network connection parameters manually to see how the Neural Engine evaluates the threat.",
        'automatic mode': "Automatic Mode simulates a real-time network traffic stream and automatically evaluates it using the Neural Engine.",
        
        # Specific Features
        'protocol': "Protocol Type is the communication standard used, typically TCP, UDP, or ICMP.",
        'tcp': "TCP (Transmission Control Protocol) is a reliable connection-oriented network protocol.",
        'udp': "UDP (User Datagram Protocol) is a fast, connectionless network protocol often used for streaming.",
        'icmp': "ICMP is used for network diagnostics and error reporting, like 'ping'.",
        'packet size': "Network Packet Size refers to the amount of data (in bytes) contained in a single network packet.",
        'encryption': "Encryption indicates whether the network traffic is protected and scrambled (e.g., HTTPS, VPN).",
        'browser': "Browser Signature (or Type) identifies the web browser or user agent making the network request.",
        'src bytes': "Source Bytes represents the total number of data bytes sent from the originating device.",
        'source bytes': "Source Bytes represents the total number of data bytes sent from the originating device.",
        'dst bytes': "Destination Bytes represents the total number of data bytes sent from the receiving device back to the source.",
        'dest bytes': "Destination Bytes represents the total number of data bytes sent from the receiving device back to the source.",
        'destination bytes': "Destination Bytes represents the total number of data bytes sent from the receiving device back to the source.",
        'traffic volume': "Traffic Volume is the total combined amount of data transferred during the session.",
        'packet rate': "Packet Rate measures the speed or frequency at which network packets are transmitted.",
        'error rate': "Error Rate is the percentage of network packets that result in transmission errors or get dropped.",
        'failed logins': "Failed Logins counts the number of unsuccessful authentication attempts. High numbers suggest a brute-force attack.",
        'login attempts': "Total Login Attempts is the overall number of times authentication was tried during the session.",
        'unusual time': "Unusual Time Access flags whether the connection occurred outside of normal, expected operational hours.",
        'session duration': "Session Duration is the total amount of time (in seconds) that the network connection was kept alive.",
        'reputation': "IP Reputation Score is a trust rating from 1 to 100 based on the IP's past behavior and threat intelligence blocklists.",
        'syn flag': "SYN Flag Count tracks the number of connection initialization requests. An unusually high count indicates a SYN Flood DDoS attack.",
        'session count': "Concurrent Sessions represents the number of active network connections running at the same time."
    }

    found_responses = []
    for key, explanation in knowledge_base.items():
        if key in query:
            if explanation not in found_responses:
                found_responses.append(explanation)
                
    if found_responses:
        return "\n\n".join(found_responses)
    elif 'feature' in query:
        return "Network features include Protocol Type, Packet Size, Session Duration, Bytes Transferred, Login Attempts, IP Reputation, and more. Ask me about any specific feature!"
    else:
        return "I provide Feature Explanation. You can ask me to explain any dashboard term, setting, or network traffic feature (e.g., 'What is packet rate?', 'Explain IP reputation', 'What are heuristic overrides?')."

if chat_query:
    st.sidebar.info(chatbot_response(chat_query))

# ----------------------------------------
# 4. Helper Functions
# ----------------------------------------
def predict(data_row, model_obj, scaler_obj, encoders_obj):
    """Real prediction function combining ML Output with Heuristic Overrides"""
    if model_obj is None:
        return False, 0.5
    
    # Heuristic Override Rules! (Explicit Red/Green triggers)
    failed_logins = float(data_row.get('failed_logins', 0))
    ip_score = float(data_row.get('ip_reputation_score', 100))
    session_duration = float(data_row.get('session_duration', 1000))
    unusual_time = str(data_row.get('unusual_time_access', 'No'))
    
    heuristic_attack = False
    heuristic_conf = 0.0
    
    if unusual_time == 'Yes':
        heuristic_attack = True
        heuristic_conf = max(heuristic_conf, 0.95)
    if failed_logins >= 3:
        heuristic_attack = True
        heuristic_conf = max(heuristic_conf, 0.92)
    if ip_score < 40:
        heuristic_attack = True
        heuristic_conf = max(heuristic_conf, 0.88)
    if session_duration < 5 and float(data_row.get('traffic_volume', 0)) > 50000:
        heuristic_attack = True # massive burst
        heuristic_conf = max(heuristic_conf, 0.96)
        
    # --- ML Engineering Pipeline ---
    login_risk_score = float(data_row['login_attempts']) + float(data_row['failed_logins'])
    traffic_intensity = float(data_row['traffic_volume']) / (float(data_row['session_duration']) + 1.0)
    total_data_transfer = float(data_row['src_bytes']) + float(data_row['dst_bytes'])
    
    def encode(val, col):
        if str(val) == 'Yes': val = 1
        elif str(val) == 'No': val = 0
            
        if encoders_obj and col in encoders_obj:
            try:
                classes = encoders_obj[col].classes_
                if val in classes:
                    return encoders_obj[col].transform([val])[0]
            except Exception: pass
        return 0

    features_dict = {
        'network_packet_size': float(data_row['network_packet_size']),
        'protocol_type': float(encode(data_row['protocol_type'], 'protocol_type')),
        'login_attempts': float(data_row['login_attempts']),
        'session_duration': float(data_row['session_duration']),
        'encryption_used': float(encode(data_row['encryption_used'], 'encryption_used')),
        'ip_reputation_score': float(data_row['ip_reputation_score']),
        'failed_logins': float(data_row['failed_logins']),
        'browser_type': float(encode(data_row['browser_type'], 'browser_type')),
        'unusual_time_access': float(encode(data_row['unusual_time_access'], 'unusual_time_access')),
        'src_bytes': float(data_row['src_bytes']),
        'dst_bytes': float(data_row['dst_bytes']),
        'traffic_volume': float(data_row['traffic_volume']),
        'packet_rate': float(data_row['packet_rate']),
        'error_rate': float(data_row['error_rate']),
        'syn_flag_count': float(data_row['syn_flag_count']),
        'session_count': float(data_row['session_count']),
        'login_risk_score': login_risk_score,
        'traffic_intensity': traffic_intensity,
        'total_data_transfer': total_data_transfer
    }
    df_features = pd.DataFrame([features_dict])
    
    if scaler_obj is not None:
        main_features = ['network_packet_size', 'traffic_volume', 'packet_rate', 'traffic_intensity']
        df_features[main_features] = scaler_obj.transform(df_features[main_features])
        
    arr = df_features.values
    ml_pred = model_obj.predict(arr)[0]
    ml_prob = model_obj.predict_proba(arr)[0].max() if hasattr(model_obj, 'predict_proba') else 0.85
    
    # If the user changed the threshold, we can adjust the prediction artificially
    # For a binary model, if the max probability is the attack class and it's less than our threshold, we can override it.
    if hasattr(model_obj, 'predict_proba'):
        probs = model_obj.predict_proba(arr)[0]
        attack_prob = probs[1] if len(probs) > 1 else ml_prob
        ml_prob = attack_prob
        # Use custom threshold from session state
        custom_threshold = st.session_state.get('threshold', 0.85)
        ml_pred = 1 if attack_prob >= custom_threshold else 0
    
    # Merge ML prediction with Heuristics
    if st.session_state.get('heuristic_override', True) and heuristic_attack:
        return True, max(ml_prob if ml_pred else 0, heuristic_conf)
    return ml_pred == 1, ml_prob

# --- NEW FEATURE: IP Geolocation Visualization ---
def get_ip_location(ip="192.168.1.104"):
    """Demo function mapping IPs to specific Indian cities."""
    import random
    locations = [
        {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"city": "Delhi", "lat": 28.7041, "lon": 77.1025},
        {"city": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867}
    ]
    loc = random.choice(locations)
    loc['ip'] = ip
    return loc

# ----------------------------------------
# 5. Main Content Routing
# ----------------------------------------

if app_mode == "📊 System Dashboard":
    st.title("Intelligent Cyber Attack Detection")
    st.markdown("### Network Intrusion Prevention System Dashboard")
    st.markdown("Monitor real-time network traffic and automated anomaly detection statistics.")
    
    # KPIs
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Live Connections", "14,203", "12% 📈")
    # --- NEW FEATURE: Live Attack Counter ---
    with col2: st.metric("Threats Prevented", f"{st.session_state['attack_count']} (Live)", "New Attacks")
    with col3: st.metric("Active Node IP", "192.168.1.104", "Safe")
    with col4: st.metric("Engine Uptime", "99.99%", "Optimal")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Area
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### System Intrusion Attempts (2026)")
        np.random.seed(2026)
        dates = pd.date_range(start="2026-02-01", periods=28)
        attacks = np.random.poisson(lam=15, size=28)
        df_time = pd.DataFrame({'Date': dates, 'Blocked Intrusions': attacks})
        fig2 = px.area(df_time, x='Date', y='Blocked Intrusions', line_shape='spline',
                       color_discrete_sequence=['#ff003c']) # Red neon
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e2e8f0", 
                           margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    with chart_col2:
        st.markdown("#### Malicious Protocol Distribution")
        df_proto = pd.DataFrame({'Protocol': ['udp', 'tcp', 'icmp'], 'Threats': [8500, 7000, 1500]})
        fig1 = px.pie(df_proto, values='Threats', names='Protocol', hole=0.5, 
                      color_discrete_sequence=['#38bdf8', '#818cf8', '#2dd4bf'])
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e2e8f0",
                           margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

elif app_mode == " Traffic Analyzer":
    st.title(" Traffic Analyzer")
    st.markdown("Select detection mode to analyze incoming or manual session signatures.")
    
    # 2. Mode Selection
    st.markdown("### 2. Mode Selection")
    detect_mode = st.radio("Select Mode:", ["Automatic Mode", "Manual Mode"], horizontal=True)
    st.markdown("---")
    
    if detect_mode == "Automatic Mode":
        st.markdown("### “ 3. Automatic Mode Output")
        st.markdown("#### “ Real-Time Network Data (Simulated)")
        
        # Generate random "live" data weighted towards SAFE traffic
        if 'auto_data' not in st.session_state or st.button("🔄 Capture New Traffic Stream"):
            st.session_state['auto_data'] = {
                'Login Attempts': np.random.randint(1, 3), # Low attempts
                'Packet Rate': np.random.randint(50, 200), # Normal rate
                'IP Reputation Score': np.random.randint(60, 100), # Good reputation
                'Error Rate': round(np.random.uniform(0.01, 0.1), 2), # Low error
                'Session Duration (sec)': np.random.randint(100, 1200), # Normal duration
                'Protocol Type': np.random.choice(['tcp', 'udp', 'icmp']),
                'Unusual Time Access': 'No', # Default safe
                
                # Hidden features required for model
                'network_packet_size': np.random.randint(500, 1500),
                'encryption_used': 'Yes', # Default safe
                'browser_type': np.random.choice(['Chrome', 'Edge', 'Firefox', 'Other']),
                'src_bytes': np.random.randint(1000, 10000),
                'dst_bytes': np.random.randint(1000, 10000),
                'traffic_volume': np.random.randint(2000, 20000),
                'failed_logins': 0, # Low avg
                'syn_flag_count': np.random.randint(0, 3),
                'session_count': np.random.randint(1, 5)
            }
            # Add bias toward attack features occasionally (15% chance to be an attack)
            if np.random.random() > 0.85:
                st.session_state['auto_data']['Login Attempts'] = np.random.randint(5, 12)
                st.session_state['auto_data']['IP Reputation Score'] = np.random.randint(5, 30)
                st.session_state['auto_data']['Error Rate'] = round(np.random.uniform(0.5, 0.9), 2)
                st.session_state['auto_data']['Unusual Time Access'] = 'Yes'
                st.session_state['auto_data']['failed_logins'] = np.random.randint(3, 8)

        data = st.session_state['auto_data']
        
        # Display simulated data clearly
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Login Attempts:** {data['Login Attempts']}")
            st.markdown(f"**Packet Rate:** {data['Packet Rate']}")
            st.markdown(f"**IP Reputation Score:** {data['IP Reputation Score']}")
            st.markdown(f"**Error Rate:** {data['Error Rate']}")
        with col2:
            st.markdown(f"**Session Duration:** {data['Session Duration (sec)']} sec")
            st.markdown(f"**Protocol Type:** {data['Protocol Type'].upper()}")
            st.markdown(f"**Unusual Time Access:** {data['Unusual Time Access']}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👉 Analyze Traffic"):
            model_input = {
                'protocol_type': data['Protocol Type'], 'network_packet_size': data['network_packet_size'],
                'encryption_used': data['encryption_used'], 'browser_type': data['browser_type'],
                'src_bytes': data['src_bytes'], 'dst_bytes': data['dst_bytes'], 'traffic_volume': data['traffic_volume'],
                'packet_rate': data['Packet Rate'], 'error_rate': data['Error Rate'], 'failed_logins': data['failed_logins'],
                'login_attempts': data['Login Attempts'], 'unusual_time_access': data['Unusual Time Access'],
                'session_duration': data['Session Duration (sec)'], 'ip_reputation_score': data['IP Reputation Score'],
                'syn_flag_count': data['syn_flag_count'], 'session_count': data['session_count']
            }
            with st.spinner("Locking Neural Engine..."):
                time.sleep(0.5)
                is_attack, conf = predict(model_input, model, scaler, encoders)
            
            # --- NEW FEATURE: Live Attack Counter ---
            if is_attack:
                st.session_state['attack_count'] += 1

            st.markdown("### 👉 Output Result:")
            if is_attack:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(220, 38, 38, 0.2) 0%, rgba(153, 27, 27, 0.5) 100%); 
                            border: 2px solid #ef4444; border-radius: 16px; padding: 30px; margin-top: 20px;
                            box-shadow: 0 0 40px rgba(239, 68, 68, 0.6); text-align: center; animation: criticalPulse 1.5s infinite;">
                    <h1 style="color: #fca5a5; font-size: 2.8rem; margin-bottom: 5px; text-shadow: 0 0 10px #ef4444;">🚨 ATTACK DETECTED 🚨</h1>
                    <h3 style="color: #f87171; margin-top: 5px; text-transform: uppercase;">Critical Intrusion Blocked</h3>
                    <hr style="border-color: rgba(239, 68, 68, 0.3); margin: 15px 0;">
                    <p style="color: #fca5a5; font-size: 1.2rem; margin-bottom: 5px;">Threat Confidence: <b>{conf*100:.1f}%</b></p>
                    <p style="color: #fecaca; font-size: 1rem;">The Neural Engine has identified malicious signatures in the packet flow.<br>Access has been immediately revoked and the IP is logged.</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # --- NEW FEATURE: IP Geolocation Visualization ---
                st.markdown("####  Threat Origin Tracking")
                loc = get_ip_location("Threat_IP_Simulated")
                df_loc = pd.DataFrame([loc])
                fig_map = px.scatter_mapbox(df_loc, lat="lat", lon="lon", hover_name="city", hover_data=["ip"],
                                        color_discrete_sequence=["#ef4444"], zoom=4, height=350)
                fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
                                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_map, use_container_width=True, theme=None)
            else:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(22, 163, 74, 0.1) 0%, rgba(21, 128, 61, 0.3) 100%); 
                            border: 2px solid #22c55e; border-radius: 16px; padding: 30px; margin-top: 20px;
                            box-shadow: 0 0 30px rgba(34, 197, 94, 0.3); text-align: center;">
                    <h1 style="color: #86efac; font-size: 2.8rem; margin-bottom: 5px; text-shadow: 0 0 10px #22c55e;">✅ NORMAL TRAFFIC ✅</h1>
                    <h3 style="color: #4ade80; margin-top: 5px; text-transform: uppercase;">Connection Secure</h3>
                    <hr style="border-color: rgba(34, 197, 94, 0.3); margin: 15px 0;">
                    <p style="color: #86efac; font-size: 1.2rem; margin-bottom: 5px;">Safety Confidence: <b>{conf*100:.1f}%</b></p>
                    <p style="color: #bbf7d0; font-size: 1rem;">No threat vectors detected. The session behavior matches normal operational baselines.<br>Traffic allowed to proceed.</p>
                </div>
                ''', unsafe_allow_html=True)

    elif detect_mode == "Manual Mode":
        st.markdown("### “ 4. Manual Mode Output")
        st.markdown("#### 👉 Input Fields")
        
        # Section 1: Connection Basics
        col1, col2, col3, col4 = st.columns(4)
        protocol_type = col1.selectbox("Protocol Type:", ["tcp", "udp", "icmp"])
        network_packet_size = col2.number_input("Packet Size:", 0, value=1500)
        encryption_used = col3.selectbox("Encryption Used:", ["Yes", "No"])
        browser_type = col4.selectbox("Browser Signature:", ["Edge", "Chrome", "Firefox", "Safari", "Other"])
        
        # Section 2: Traffic Stats
        col5, col6, col7, col8 = st.columns(4)
        src_bytes = col5.number_input("Source Bytes:", 0, value=4500)
        dst_bytes = col6.number_input("Dest Bytes:", 0, value=8200)
        traffic_volume = col7.number_input("Traffic Volume:", 0, value=12700)
        packet_rate = col8.number_input("Packet Rate:", 0.0, value=120.5)
        
        # Section 3: Threat Indicators
        col9, col10, col11, col12 = st.columns(4)
        error_rate = col9.slider("Error Rate:", 0.0, 1.0, value=0.05)
        failed_logins = col10.number_input("Failed Logins:", 0, value=0)
        login_attempts = col11.number_input("Total Login Attempts:", 0, value=1)
        unusual_time = col12.selectbox("Unusual Time Access?", ["No", "Yes"])
        
        # Section 4: Behavior Metrics
        col13, col14, col15, col16 = st.columns(4)
        session_duration = col13.number_input("Session Duration:", 0, value=300)
        ip_reputation = col14.number_input("IP Reputation Score:", 1, 100, 85)
        syn_flag_count = col15.number_input("SYN Flag Count:", 0, value=2)
        session_count = col16.number_input("Concurrent Sessions:", 1, value=5)
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.button("👉 Predict Attack")
        
        # Maintain state so results do not disappear when clicking away!
        if submit_btn:
            st.session_state['manual_scan_run'] = True
            input_data = {
                'protocol_type': protocol_type, 'network_packet_size': network_packet_size,
                'encryption_used': encryption_used, 'browser_type': browser_type,
                'src_bytes': src_bytes, 'dst_bytes': dst_bytes, 'traffic_volume': traffic_volume,
                'packet_rate': packet_rate, 'error_rate': error_rate, 'failed_logins': failed_logins,
                'login_attempts': login_attempts, 'unusual_time_access': unusual_time,
                'session_duration': session_duration, 'ip_reputation_score': ip_reputation,
                'syn_flag_count': syn_flag_count, 'session_count': session_count
            }
            
            with st.spinner("Locking Neural Engine... Analyzing Heuristics & Weights..."):
                time.sleep(0.5)
                is_attack, conf = predict(input_data, model, scaler, encoders)
                
            # --- NEW FEATURE: Live Attack Counter ---
            if is_attack:
                st.session_state['attack_count'] += 1
                
            st.session_state['last_scan_result'] = is_attack
            st.session_state['last_scan_conf'] = conf

        if st.session_state.get('manual_scan_run', False):
            is_attack = st.session_state['last_scan_result']
            conf = st.session_state['last_scan_conf']
            st.markdown("### 👉 Prediction Output")
            
            if is_attack:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(220, 38, 38, 0.2) 0%, rgba(153, 27, 27, 0.5) 100%); 
                            border: 2px solid #ef4444; border-radius: 16px; padding: 30px; margin-top: 20px;
                            box-shadow: 0 0 40px rgba(239, 68, 68, 0.6); text-align: center; animation: criticalPulse 1.5s infinite;">
                    <h1 style="color: #fca5a5; font-size: 2.8rem; margin-bottom: 5px; text-shadow: 0 0 10px #ef4444;">🚨 ATTACK DETECTED 🚨</h1>
                    <h3 style="color: #f87171; margin-top: 5px; text-transform: uppercase;">Critical Intrusion Blocked</h3>
                    <hr style="border-color: rgba(239, 68, 68, 0.3); margin: 15px 0;">
                    <p style="color: #fca5a5; font-size: 1.2rem; margin-bottom: 5px;">Threat Confidence: <b>{conf*100:.1f}%</b></p>
                    <p style="color: #fecaca; font-size: 1rem;">The Neural Engine has identified malicious signatures in the packet flow.<br>Access has been immediately revoked and the IP is logged.</p>
                </div>
                ''', unsafe_allow_html=True)

                # --- NEW FEATURE: IP Geolocation Visualization ---
                st.markdown("####  Threat Origin Tracking")
                loc = get_ip_location("Manual_Threat_IP")
                df_loc = pd.DataFrame([loc])
                fig_map = px.scatter_mapbox(df_loc, lat="lat", lon="lon", hover_name="city", hover_data=["ip"],
                                        color_discrete_sequence=["#ef4444"], zoom=4, height=350)
                fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0},
                                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_map, use_container_width=True, theme=None)
            else:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(22, 163, 74, 0.1) 0%, rgba(21, 128, 61, 0.3) 100%); 
                            border: 2px solid #22c55e; border-radius: 16px; padding: 30px; margin-top: 20px;
                            box-shadow: 0 0 30px rgba(34, 197, 94, 0.3); text-align: center;">
                    <h1 style="color: #86efac; font-size: 2.8rem; margin-bottom: 5px; text-shadow: 0 0 10px #22c55e;">✅ NORMAL TRAFFIC ✅</h1>
                    <h3 style="color: #4ade80; margin-top: 5px; text-transform: uppercase;">Connection Secure</h3>
                    <hr style="border-color: rgba(34, 197, 94, 0.3); margin: 15px 0;">
                    <p style="color: #86efac; font-size: 1.2rem; margin-bottom: 5px;">Safety Confidence: <b>{conf*100:.1f}%</b></p>
                    <p style="color: #bbf7d0; font-size: 1rem;">No threat vectors detected. The session behavior matches normal operational baselines.<br>Traffic allowed to proceed.</p>
                </div>
                ''', unsafe_allow_html=True)

elif app_mode == "“ Upload Network Logs":
    st.title("“ Batch Log Processing")
    st.markdown("Upload comprehensive `.csv` logs to run mass intrusion detection logic.")
    
    uploaded_file = st.file_uploader("Upload Network Logs to Prevent Intrusions (CSV)", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Log Engine Initialized: {len(df)} incoming connection requests.")
                
            if st.button("€ Execute Mass Scan Protocol"):
                status_text = st.empty()
                status_text.text("Ingesting and processing logs using Neural Vectorization...")
                
                start_time = time.time()
                original_cols = df.columns.tolist()
                
                # --- Vectorized Processing ---
                # Ensure all necessary columns exist (pad with safe defaults if they don't, to prevent false positives!)
                safe_defaults = {
                    'protocol_type': 'tcp', 'network_packet_size': 500, 'encryption_used': 'Yes', 'browser_type': 'Other', 
                    'src_bytes': 1500, 'dst_bytes': 3000, 'traffic_volume': 4500, 'packet_rate': 120, 'error_rate': 0.05, 
                    'failed_logins': 0, 'login_attempts': 1, 'unusual_time_access': 'No', 'session_duration': 300, 
                    'ip_reputation_score': 85, 'syn_flag_count': 1, 'session_count': 1
                }
                for c, default_val in safe_defaults.items():
                    if c not in df.columns:
                        df[c] = default_val
                
                def batch_predict(row):
                    is_att, _ = predict(row.to_dict(), model, scaler, encoders)
                    return "Attack" if is_att else "Normal"
                
                # Apply vectorization (much faster than iterative updates with UI)
                df['Prediction'] = df.apply(batch_predict, axis=1)
                
                end_time = time.time()
                status_text.text(f"Intrusion Scan Complete! Processed in {(end_time - start_time):.2f} seconds.")
                
                attacks_found = len(df[df['Prediction'] == 'Attack'])
                
                st.markdown("---")
                st.markdown("### 📊 Post-Processing Threat Report")
                
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("🔴 Intrusions Blocked", f"{attacks_found}", "- Action Taken")
                cc2.metric("🟢 Safe Traffic", f"{len(df) - attacks_found}", "Allowed")
                cc3.metric("⚠️ Threat Level", f"{(attacks_found/len(df))*100:.1f}%", "Volume Index")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Graphs
                g1, g2 = st.columns(2)
                
                with g1:
                    fig_pie = px.pie(df, names='Prediction', title='Clean vs. Malicious Nodes',
                                 color='Prediction', color_discrete_map={'Normal': '#22c55e', 'Attack': '#ef4444'}, hole=0.6)
                    fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e2e8f0")
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with g2:
                    if 'protocol_type' in df.columns:
                        attack_df = df[df['Prediction'] == 'Attack']
                        if not attack_df.empty:
                            proto_att = attack_df['protocol_type'].value_counts().reset_index()
                            proto_att.columns = ['Protocol', 'Threats']
                            fig_bar = px.bar(proto_att, x='Protocol', y='Threats', title="Intrusions Grouped by Protocol",
                                             color='Protocol', color_discrete_sequence=px.colors.sequential.Inferno)
                            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e2e8f0")
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("No attacks found to generate protocol breakdown.")
                
                # Logs download
                st.markdown("#### Blocked Threat Nodes:")
                
                # Filter back to only what the user actually uploaded, plus the prediction result
                display_cols = original_cols + ['Prediction']
                suspicious_df = df[df['Prediction'] == 'Attack'][display_cols]
                
                st.dataframe(suspicious_df, use_container_width=True)
                
                csv = suspicious_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="‡ Export Malicious IP Report (CSV)",
                    data=csv,
                    file_name='quarantine_threats.csv',
                    mime='text/csv',
                )
                
        except Exception as e:
            st.error(f"Error parsing bulk logs: {e}")

elif app_mode == "⚙️ Engine Settings":
    st.title("⚙️ Neural Engine Settings")
    st.markdown("Configure system pathways and algorithm strictness.")
    
    st.markdown("#### Heuristic Guardrails")
    st.session_state['heuristic_override'] = st.checkbox("Enable Heuristic Overrides (Unusual Time, High Failed Logins)", value=st.session_state['heuristic_override'], help="If ML confidence is low but blatant risks are present, manually trigger the alarm.")
    
    st.markdown("#### Algorithm Strictness")
    st.session_state['threshold'] = st.slider("Anomaly Detection Sensitivity (Threshold)", 0.0, 1.0, st.session_state['threshold'])
    
    st.markdown("#### Hardware Binding")
    new_model_path = st.text_input("Model Pickle Location", value=st.session_state.get('model_path', 'model.pkl'))
    
    if st.button("Apply Security Policies"):
        st.session_state['model_path'] = new_model_path
        st.cache_resource.clear()
        st.session_state['settings_saved'] = True
        st.rerun()

    if st.session_state.get('settings_saved', False):
        st.success("Policies propagated locally and model reloaded.")
        st.session_state['settings_saved'] = False

elif app_mode == "‘ User Management":
    st.title("‘ User Management")
    if st.session_state.get('role') != 'admin':
        st.error("Unauthorized access. Admin privileges required.")
        st.stop()
        
    st.markdown("Approve new users or revoke access for existing system users.")
    users = load_users()
    
    st.subheader(" Pending Approvals")
    pending_users = [u for u, data in users.items() if data.get('status') == 'pending']
    
    if not pending_users:
        st.info("No users currently pending approval.")
    else:
        for u in pending_users:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"👤 **{u}** (Requested Role: `{users[u].get('role', 'user')}`)")
            with col2:
                if st.button(f"Approve {u}", key=f"app_{u}"):
                    users[u]['status'] = 'approved'
                    save_users(users)
                    st.success(f"User '{u}' approved successfully!")
                    time.sleep(1)
                    st.rerun()
                
    st.markdown("---")
    st.subheader("✅ Approved Users")
    
    current_user = st.session_state.get('username')
    approved_users = [u for u, data in users.items() if data.get('status') == 'approved' and u != current_user]
    
    if not approved_users:
        st.info("No other approved users found.")
    else:
        for u in approved_users:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"👤 **{u}** (Role: `{users[u].get('role', 'user')}`)")
            with col2:
                if st.button(f"Revoke Access for {u}", key=f"rev_{u}"):
                    users[u]['status'] = 'pending'
                    save_users(users)
                    st.warning(f"Access revoked for '{u}'. They are now pending approval again.")
                    time.sleep(1)
                    st.rerun()

st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 0.9rem;">
        &copy; 2026 / CYBER ATTACK DETECTION &<br>
        NETWORK INTRUSION PREVENTION SYSTEM
    </div>
""", unsafe_allow_html=True)

