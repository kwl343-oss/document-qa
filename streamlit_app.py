import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import fitz
import pandas as pd

# ========================================
# PAGE CONFIG & INITIALIZATION
# ========================================
st.set_page_config(
    page_title="VCaaS – Deal Intake & Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

EXTRACT_SCHEMA = {
    "company": None,
    "stage": None,
    "sector": None,
    "raise_amount_usd": None,
    "arr_usd": None,
    "growth_rate_pct": None,
    "runway_months": None,
    "notes": None
}

# ========================================
# APPLE DESIGN SYSTEM CSS
# ========================================
st.markdown("""
    <style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }

    :root {
        --primary: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark: #0b0f1a;
        --card: #131929;
        --card-border: #1e2a40;
        --text: #e2e8f0;
        --muted: #475569;
        --subtle: #64748b;
    }
    
    /* ===== DARK BASE ===== */
    .stApp { background: #0b0f1a !important; color: #e2e8f0 !important; }
    .main .block-container { padding-top: 1.5rem !important; max-width: 100% !important; }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] { background: #0d1424 !important; border-right: 1px solid #1e2a40 !important; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] hr { border-color: #1e2a40 !important; }
    [data-testid="stSidebarNav"] { display: none; }

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 { color: #f1f5f9 !important; font-weight: 600 !important; letter-spacing: -0.02em; }
    p, .stMarkdown p, .stMarkdown li { color: #cbd5e1 !important; }
    label { color: #94a3b8 !important; font-size: 0.85em !important; }
    .stCaption p { color: #64748b !important; }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1a2035 !important; color: #e2e8f0 !important;
        border: 1px solid #2a3550 !important; border-radius: 10px !important;
        font-size: 0.92em !important; padding: 0.6rem 0.85rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #1a2035 !important; color: #e2e8f0 !important;
        border: 1px solid #2a3550 !important; border-radius: 10px !important;
    }
    [data-baseweb="select"] * { color: #e2e8f0 !important; background: #1a2035 !important; }
    [data-baseweb="menu"] { background: #1a2035 !important; border: 1px solid #2a3550 !important; }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: #1a2035 !important; color: #cbd5e1 !important;
        border: 1px solid #2a3550 !important; border-radius: 10px !important;
        font-weight: 500 !important; font-size: 0.88em !important;
        padding: 0.55rem 1.1rem !important; transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background: #243050 !important; border-color: #3b82f6 !important;
        color: #93c5fd !important;
    }
    .stButton > button[kind="primary"] {
        background: #2563eb !important; color: white !important;
        border: none !important; box-shadow: 0 0 20px rgba(37,99,235,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover { background: #1d4ed8 !important; }

    /* ===== METRICS ===== */
    [data-testid="metric-container"] {
        background: #131929 !important; border: 1px solid #1e2a40 !important;
        border-radius: 14px !important; padding: 1.1rem 1.25rem !important;
    }
    [data-testid="metric-container"] label { color: #475569 !important; font-size: 0.72em !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
    [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] { color: #64748b !important; }

    /* ===== PROGRESS ===== */
    .stProgress > div > div > div { background: #1e2a40 !important; border-radius: 999px !important; height: 5px !important; }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #3b82f6, #10b981) !important; border-radius: 999px !important; }

    /* ===== DIVIDER ===== */
    hr, [data-testid="stDivider"] { border-color: #1e2a40 !important; margin: 1.5rem 0 !important; }

    /* ===== EXPANDER ===== */
    [data-testid="stExpander"] { background: #131929 !important; border: 1px solid #1e2a40 !important; border-radius: 12px !important; }
    [data-testid="stExpander"] summary { color: #e2e8f0 !important; }

    /* ===== INFO/ALERTS ===== */
    [data-testid="stInfo"] { background: rgba(59,130,246,0.08) !important; border: 1px solid rgba(59,130,246,0.25) !important; border-radius: 12px !important; color: #93c5fd !important; }
    [data-testid="stWarning"] { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 12px !important; }
    [data-testid="stSuccess"] { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 12px !important; }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] { background: #131929 !important; border: 2px dashed #2a3550 !important; border-radius: 12px !important; }
    [data-testid="stFileUploader"] * { color: #64748b !important; }

    /* ===== CHAT ===== */
    [data-testid="stChatInput"] > div { background: #1a2035 !important; border: 1px solid #2a3550 !important; border-radius: 12px !important; }
    [data-testid="stChatMessage"] { background: #131929 !important; border: 1px solid #1e2a40 !important; border-radius: 12px !important; }

    /* ===== FORM SUBMIT ===== */
    [data-testid="stFormSubmitButton"] > button { background: #2563eb !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }

    /* ===== CUSTOM COMPONENTS ===== */

    /* Breadcrumb */
    .vc-breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 0.82em; color: #475569; margin-bottom: 0.5rem; }
    .vc-breadcrumb .sep { color: #2a3550; }
    .vc-breadcrumb .crumb { color: #475569; cursor: pointer; }
    .vc-breadcrumb .crumb:hover { color: #94a3b8; }
    .vc-breadcrumb .current { color: #e2e8f0; font-weight: 600; }

    /* Decision badges */
    .badge-watch { display: inline-flex; align-items: center; gap: 6px; background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); padding: 4px 12px; border-radius: 999px; font-size: 0.78em; font-weight: 700; letter-spacing: 0.06em; }
    .badge-proceed { display: inline-flex; align-items: center; gap: 6px; background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.25); padding: 4px 12px; border-radius: 999px; font-size: 0.78em; font-weight: 700; letter-spacing: 0.06em; }
    .badge-pass { display: inline-flex; align-items: center; gap: 6px; background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); padding: 4px 12px; border-radius: 999px; font-size: 0.78em; font-weight: 700; letter-spacing: 0.06em; }

    /* Deal pills */
    .pills-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1.1rem; }
    .pill { display: flex; flex-direction: column; background: #131929; border: 1px solid #1e2a40; border-radius: 10px; padding: 7px 13px; min-width: 90px; }
    .pill-lbl { font-size: 0.6em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3a4a65; margin-bottom: 3px; }
    .pill-val { font-size: 0.88em; font-weight: 600; color: #e2e8f0; }
    .pv-green { color: #34d399; } .pv-orange { color: #fbbf24; } .pv-red { color: #f87171; } .pv-blue { color: #60a5fa; } .pv-purple { color: #a78bfa; }

    /* Dark card */
    .vc-card { background: #131929; border: 1px solid #1e2a40; border-radius: 16px; padding: 1.4rem; margin-bottom: 1rem; }
    .vc-card-title { font-size: 0.68em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3a4a65; margin-bottom: 1rem; }

    /* Personalization notice */
    .pers-notice { background: rgba(59,130,246,0.07); border: 1px solid rgba(59,130,246,0.2); border-radius: 11px; padding: 11px 15px; margin-bottom: 1.1rem; display: flex; align-items: flex-start; gap: 10px; font-size: 0.845em; color: #93c5fd; line-height: 1.5; }
    .pers-notice strong { color: #e2e8f0; }

    /* Big score display */
    .big-score { display: flex; align-items: baseline; gap: 3px; margin-bottom: 4px; line-height: 1; }
    .bs-num { font-size: 2.6em; font-weight: 800; letter-spacing: -0.04em; }
    .bs-pct { font-size: 1.8em; font-weight: 800; letter-spacing: -0.04em; }
    .bs-denom { font-size: 1em; color: #3a4a65; font-weight: 500; }
    .bs-sub { font-size: 0.78em; color: #475569; margin-bottom: 1rem; }

    /* Thin progress bar */
    .bar-track { background: #1e2a40; height: 4px; border-radius: 999px; overflow: hidden; flex: 1; }
    .bar-fill { height: 100%; border-radius: 999px; }
    .score-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; }
    .sbl { font-size: 0.82em; color: #64748b; min-width: 78px; flex-shrink: 0; }
    .sbv { font-size: 0.82em; font-weight: 700; min-width: 26px; text-align: right; flex-shrink: 0; }

    /* Signal items */
    .signal { display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; border-radius: 9px; margin-bottom: 7px; }
    .sig-pos { background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.14); }
    .sig-neg { background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.14); }
    .sig-icon { width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.68em; font-weight: 700; flex-shrink: 0; margin-top: 2px; }
    .si-up { background: rgba(16,185,129,0.18); color: #34d399; }
    .si-dn { background: rgba(239,68,68,0.18); color: #f87171; }
    .sig-body { flex: 1; }
    .sig-title { font-size: 0.875em; font-weight: 600; color: #e2e8f0; margin-bottom: 2px; }
    .sig-desc { font-size: 0.775em; color: #475569; line-height: 1.4; }
    .sig-delta { font-size: 0.78em; font-weight: 700; flex-shrink: 0; margin-top: 2px; }
    .sd-pos { color: #34d399; } .sd-neg { color: #f87171; }

    /* Deal info panel */
    .di-row { display: flex; justify-content: space-between; align-items: baseline; padding: 9px 0; border-bottom: 1px solid #141c2e; }
    .di-row:last-child { border-bottom: none; }
    .di-lbl { font-size: 0.82em; color: #3a4a65; }
    .di-val { font-size: 0.875em; font-weight: 600; color: #e2e8f0; text-align: right; max-width: 60%; }

    /* Benchmark */
    .bench-row { display: flex; align-items: center; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid #141c2e; font-size: 0.82em; }
    .bench-row:last-child { border-bottom: none; }
    .bl { color: #475569; } .bv { font-weight: 700; color: #e2e8f0; } .ba { color: #334155; font-size: 0.9em; }

    /* Urgency banner */
    .urgency { display: flex; align-items: center; gap: 9px; border-radius: 10px; padding: 10px 14px; margin-bottom: 0.9rem; font-size: 0.84em; font-weight: 500; }

    /* Section labels */
    .sec-lbl { font-size: 0.68em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3a4a65; margin-bottom: 0.75rem; margin-top: 0.5rem; }

    /* Pipeline sidebar */
    .pl-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-bottom: 1rem; }
    .pl-metric { background: #131929; border: 1px solid #1e2a40; border-radius: 10px; padding: 10px; text-align: center; }
    .pl-num { font-size: 1.5em; font-weight: 800; color: #e2e8f0; line-height: 1; }
    .pl-lbl { font-size: 0.65em; color: #3a4a65; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.07em; }

    /* Nav tab row */
    .tab-row { display: flex; border-bottom: 1px solid #1e2a40; margin-bottom: 1.5rem; gap: 2px; }

    /* Main title */
    .main-title { font-size: 1.5em; font-weight: 700; color: #f1f5f9; letter-spacing: -0.025em; }
    .subtitle { font-size: 0.85em; color: #475569; font-weight: 400; }

    /* Form sections */
    .form-section { background: #131929; border-radius: 14px; padding: 1.5rem; border: 1px solid #1e2a40; margin-bottom: 1.5rem; }
    .form-section-title { font-size: 1em; font-weight: 600; color: #e2e8f0; margin-bottom: 1.25rem; }
    .form-label { font-size: 0.9em; font-weight: 500; color: #94a3b8; margin-bottom: 0.4rem; }
    .form-hint { font-size: 0.8em; color: #475569; }

    /* Extraction preview */
    .extraction-preview { background: #0d1424; border: 1px solid #1e2a40; border-radius: 10px; padding: 1rem; margin-bottom: 1.25rem; font-family: 'Monaco', 'Courier New', monospace; font-size: 0.82em; max-height: 280px; overflow-y: auto; color: #64748b; }

    /* Status badges */
    .status-ready { display: inline-block; background: rgba(16,185,129,0.12); color: #34d399; padding: 3px 10px; border-radius: 6px; font-size: 0.72em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid rgba(16,185,129,0.2); }
    .status-pending { display: inline-block; background: rgba(245,158,11,0.12); color: #fbbf24; padding: 3px 10px; border-radius: 6px; font-size: 0.72em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid rgba(245,158,11,0.2); }

    /* Info/warning boxes */
    .info-box { background: rgba(59,130,246,0.07); border: 1px solid rgba(59,130,246,0.2); border-radius: 11px; padding: 1rem; margin-bottom: 1.25rem; color: #93c5fd; font-size: 0.9em; }
    .warning-box { background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.2); border-radius: 11px; padding: 1rem; margin-bottom: 1.25rem; color: #fbbf24; font-size: 0.9em; }

    /* Driver cards (legacy) */
    .driver-positive { background: rgba(16,185,129,0.07); border-left: 3px solid #10b981; padding: 0.9rem; border-radius: 8px; margin: 0.4rem 0; }
    .driver-negative { background: rgba(245,158,11,0.07); border-left: 3px solid #f59e0b; padding: 0.9rem; border-radius: 8px; margin: 0.4rem 0; }
    .driver-flag { background: rgba(239,68,68,0.07); border-left: 3px solid #ef4444; padding: 0.9rem; border-radius: 8px; margin: 0.4rem 0; }

    /* Column fix */
    .stColumn > div > div { width: 100%; }

    /* Scrollbar dark */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0b0f1a; }
    ::-webkit-scrollbar-thumb { background: #2a3550; border-radius: 3px; }

    </style>
""", unsafe_allow_html=True)

# ========================================
# SESSION STATE INITIALIZATION
# ========================================

# Persistent user database using JSON file
USERS_DB_FILE = "/workspaces/document-qa/users_db.json"

def load_users_db():
    """Load users database from file."""
    import os
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users_db(users_db):
    """Save users database to file."""
    with open(USERS_DB_FILE, 'w') as f:
        json.dump(users_db, f, indent=2)

# User authentication
if "users_db" not in st.session_state:
    # Load persistent user database from file
    st.session_state.users_db = load_users_db()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "login_error" not in st.session_state:
    st.session_state.login_error = None

if "auto_login_checked" not in st.session_state:
    st.session_state.auto_login_checked = False

if "investor_prefs" not in st.session_state:
    st.session_state.investor_prefs = None

if "show_prefs_onboard" not in st.session_state:
    st.session_state.show_prefs_onboard = False

if "extracted_highlights" not in st.session_state:
    st.session_state.extracted_highlights = None

if "founder_questions" not in st.session_state:
    st.session_state.founder_questions = None

if "ic_memo" not in st.session_state:
    st.session_state.ic_memo = None

if "founder_followup" not in st.session_state:
    st.session_state.founder_followup = None

if "founder_email" not in st.session_state:
    st.session_state.founder_email = None

if "saved_deals" not in st.session_state:
    st.session_state.saved_deals = []

if "deals_by_status" not in st.session_state:
    st.session_state.deals_by_status = {
        "watchlist": [],
        "active": [],
        "reviewed": [],
        "passed": []
    }

if "active_list" not in st.session_state:
    st.session_state.active_list = "watchlist"

if "deal_filters" not in st.session_state:
    st.session_state.deal_filters = {
        "stages": [],
        "sectors": [],
        "decisions": [],
        "min_arr": 0,
        "search": "",
        "sort_by": "last_updated"
    }

if "active_content" not in st.session_state:
    st.session_state.active_content = None

# Auto-login check using query params
if not st.session_state.auto_login_checked:
    st.session_state.auto_login_checked = True
    # Check if user param exists in URL
    query_params = st.query_params
    if "user" in query_params:
        username = query_params["user"]
        if username in st.session_state.users_db:
            st.session_state.current_user = username
            st.session_state.logged_in = True
            st.session_state.investor_prefs = st.session_state.users_db[username].get("investor_prefs")
            st.session_state.saved_deals = st.session_state.users_db[username].get("saved_deals", [])

# Initialize form field keys (must happen before widget creation)
for k in ["company", "stage", "sector", "raise_amount_usd", "arr_usd", "growth_rate_pct", "runway_months", "notes"]:
    if k not in st.session_state:
        st.session_state[k] = None

# Initialize analysis state
if "last_deal" not in st.session_state:
    st.session_state.last_deal = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "extracted" not in st.session_state:
    st.session_state.extracted = None

if "docs_text" not in st.session_state:
    st.session_state.docs_text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Intake"

# ========================================
# HELPER FUNCTIONS
# ========================================

def scroll_to_top():
    """Scroll page to top using JavaScript."""
    st.markdown("""
    <script>
        window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)

def set_login_cookie(username: str):
    """Set login cookie using JavaScript."""
    st.markdown(f"""
    <script>
        localStorage.setItem('vcaas_user', '{username}');
    </script>
    """, unsafe_allow_html=True)

def clear_login_cookie():
    """Clear login cookie."""
    st.markdown("""
    <script>
        localStorage.removeItem('vcaas_user');
    </script>
    """, unsafe_allow_html=True)

def login_user(username: str, password: str) -> bool:
    """Login user with username/password."""
    if username in st.session_state.users_db:
        if st.session_state.users_db[username]["password"] == password:
            st.session_state.current_user = username
            st.session_state.logged_in = True
            st.session_state.login_error = None
            # Load user's investor preferences and deals
            st.session_state.investor_prefs = st.session_state.users_db[username].get("investor_prefs")
            st.session_state.saved_deals = st.session_state.users_db[username].get("saved_deals", [])
            # Set query param for persistent login
            st.query_params["user"] = username
            set_login_cookie(username)
            return True
    return False

def auto_login_from_cookie() -> bool:
    """Try to auto-login from stored username."""
    # This would check localStorage in a real implementation
    # For now, just return False
    return False

def signup_user(username: str, password: str) -> bool:
    """Create new user account."""
    if username in st.session_state.users_db:
        return False
    
    st.session_state.users_db[username] = {
        "password": password,
        "investor_prefs": None,
        "saved_deals": [],
        "created_at": datetime.now().isoformat()
    }
    
    # Save to persistent storage
    save_users_db(st.session_state.users_db)
    
    st.session_state.current_user = username
    st.session_state.logged_in = True
    st.session_state.login_error = None
    st.session_state.saved_deals = []
    # Set query param for persistent login
    st.query_params["user"] = username
    set_login_cookie(username)
    return True

def logout_user():
    """Logout current user."""
    st.session_state.current_user = None
    st.session_state.logged_in = False
    st.session_state.investor_prefs = None
    st.session_state.login_error = None
    # Clear query param
    if "user" in st.query_params:
        del st.query_params["user"]
    clear_login_cookie()

def save_user_preferences(prefs: dict):
    """Save preferences to current user's profile."""
    if st.session_state.current_user:
        st.session_state.users_db[st.session_state.current_user]["investor_prefs"] = prefs
        st.session_state.investor_prefs = prefs
        # Save to persistent storage
        save_users_db(st.session_state.users_db)

def save_deal(deal: dict, result: dict, status: str = "reviewing"):
    """Save current deal to user's deal history."""
    import uuid
    
    deal_snapshot = {
        "id": str(uuid.uuid4())[:8],
        "company": deal.get("company", "Unknown"),
        "stage": deal.get("stage", ""),
        "sector": deal.get("sector", ""),
        "arr_usd": deal.get("arr_usd", 0),
        "prob_next_round": result.get("prob_next_round", 0),
        "decision": get_investment_decision(result.get("prob_next_round", 0))[0],
        "status": status,
        "last_updated": datetime.now().isoformat(),
        "full_deal": deal,
        "full_result": result
    }
    
    # Check if deal already exists (by company name)
    existing_idx = None
    for i, d in enumerate(st.session_state.saved_deals):
        if d.get("company") == deal.get("company"):
            existing_idx = i
            break
    
    if existing_idx is not None:
        # Update existing deal
        st.session_state.saved_deals[existing_idx] = deal_snapshot
    else:
        # Add new deal
        st.session_state.saved_deals.insert(0, deal_snapshot)
    
    # Save to user account
    if st.session_state.current_user:
        st.session_state.users_db[st.session_state.current_user]["saved_deals"] = st.session_state.saved_deals
        save_users_db(st.session_state.users_db)

def load_deal(deal_snapshot: dict):
    """Load a saved deal back into the form."""
    deal = deal_snapshot.get("full_deal", {})
    result = deal_snapshot.get("full_result", {})
    
    # Load into session state
    st.session_state.company = deal.get("company")
    st.session_state.stage = deal.get("stage")
    st.session_state.sector = deal.get("sector")
    st.session_state.raise_amount_usd = deal.get("raise_amount_usd")
    st.session_state.arr_usd = deal.get("arr_usd")
    st.session_state.growth_rate_pct = deal.get("growth_rate_pct")
    st.session_state.runway_months = deal.get("runway_months")
    st.session_state.notes = deal.get("notes")
    
    st.session_state.last_deal = deal
    st.session_state.last_result = result

def update_deal_status(deal_id: str, new_status: str):
    """Update the status of a saved deal."""
    for deal in st.session_state.saved_deals:
        if deal["id"] == deal_id:
            deal["status"] = new_status
            deal["last_updated"] = datetime.now().isoformat()
            break
    
    # Save to user account
    if st.session_state.current_user:
        st.session_state.users_db[st.session_state.current_user]["saved_deals"] = st.session_state.saved_deals
        save_users_db(st.session_state.users_db)

def save_deal_to_list(deal: dict, result: dict, status: str = None, tags: str = ""):
    """Save deal to a specific list with smart defaults based on investment decision."""
    import uuid
    
    # Auto-suggest status based on decision if not provided
    if status is None:
        decision = get_investment_decision(result.get("prob_next_round", 0))[0]
        if decision == "Proceed":
            status = "active"
        elif decision == "Watch":
            status = "watchlist"
        elif decision == "Pass":
            status = "passed"
        else:
            status = "reviewed"
    
    # Create deal snapshot
    deal_snapshot = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": status,
        "company": deal.get("company", "Unknown"),
        "stage": deal.get("stage"),
        "sector": deal.get("sector"),
        "raise_amount_usd": deal.get("raise_amount_usd"),
        "arr_usd": deal.get("arr_usd", 0),
        "growth_rate_pct": deal.get("growth_rate_pct"),
        "runway_months": deal.get("runway_months"),
        "decision": get_investment_decision(result.get("prob_next_round", 0))[0],
        "prob_next_round": result.get("prob_next_round", 0),
        "confidence": result.get("confidence", "Medium"),
        "score_breakdown": result.get("category_scores", {}),
        "missing_items": result.get("missing_metrics", []),
        "memo_text": st.session_state.ic_memo,
        "founder_followup_email": st.session_state.founder_followup,
        "notes": deal.get("notes"),
        "doc_text_len": len(st.session_state.docs_text) if st.session_state.docs_text else 0,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "full_deal": deal,
        "full_result": result
    }
    
    # Check if deal already exists (update instead of duplicate)
    existing_idx = None
    for i, d in enumerate(st.session_state.saved_deals):
        if d.get("company") == deal.get("company"):
            existing_idx = i
            break
    
    if existing_idx is not None:
        # Keep original created_at
        deal_snapshot["created_at"] = st.session_state.saved_deals[existing_idx].get("created_at", deal_snapshot["created_at"])
        deal_snapshot["id"] = st.session_state.saved_deals[existing_idx].get("id", deal_snapshot["id"])
        st.session_state.saved_deals[existing_idx] = deal_snapshot
    else:
        st.session_state.saved_deals.insert(0, deal_snapshot)
    
    # Save to user account
    if st.session_state.current_user:
        st.session_state.users_db[st.session_state.current_user]["saved_deals"] = st.session_state.saved_deals
        save_users_db(st.session_state.users_db)
    
    return status

def get_filtered_deals(status: str = None):
    """Get deals filtered by current filter settings."""
    deals = st.session_state.saved_deals
    
    # Filter by status/list
    if status:
        deals = [d for d in deals if d.get("status") == status]
    
    # Apply filters
    filters = st.session_state.deal_filters
    
    if filters["stages"]:
        deals = [d for d in deals if d.get("stage") in filters["stages"]]
    
    if filters["sectors"]:
        deals = [d for d in deals if d.get("sector") in filters["sectors"]]
    
    if filters["decisions"]:
        deals = [d for d in deals if d.get("decision") in filters["decisions"]]
    
    if filters["min_arr"] > 0:
        deals = [d for d in deals if d.get("arr_usd", 0) >= filters["min_arr"]]
    
    if filters["search"]:
        search_lower = filters["search"].lower()
        deals = [d for d in deals if search_lower in d.get("company", "").lower()]
    
    # Sort
    if filters["sort_by"] == "last_updated":
        deals = sorted(deals, key=lambda d: d.get("updated_at", ""), reverse=True)
    elif filters["sort_by"] == "probability":
        deals = sorted(deals, key=lambda d: d.get("prob_next_round", 0), reverse=True)
    elif filters["sort_by"] == "arr":
        deals = sorted(deals, key=lambda d: d.get("arr_usd", 0), reverse=True)
    
    return deals

def get_openai_client():
    """Get OpenAI client safely."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        # Try to get from sidebar input
        api_key = st.session_state.get("sidebar_api_key")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def pdf_to_text(file) -> str:
    """Extract text from PDF."""
    try:
        data = file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        parts = []
        for page in doc:
            parts.append(page.get_text("text"))
        return "\n".join(parts)
    except:
        return ""

def txt_to_text(file) -> str:
    """Extract text from TXT."""
    try:
        return file.read().decode("utf-8", errors="ignore")
    except:
        return ""

def tabular_to_text(file) -> str:
    """Extract text from CSV/Excel."""
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        return df.to_string()
    except:
        return ""

def pptx_to_text(file) -> str:
    """Extract text from PPTX."""
    try:
        from pptx import Presentation
        prs = Presentation(file)
        parts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    parts.append(shape.text)
        return "\n".join(parts)
    except:
        return ""

def extract_zip(file) -> list:
    """Extract files from a ZIP archive and return list of (filename, file_object) tuples."""
    import zipfile
    from io import BytesIO
    
    extracted_files = []
    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                # Skip directories and hidden files
                if filename.endswith('/') or filename.startswith('__MACOSX') or filename.startswith('.'):
                    continue
                
                # Extract file content
                file_data = zip_ref.read(filename)
                file_obj = BytesIO(file_data)
                file_obj.name = filename
                extracted_files.append((filename, file_obj))
        return extracted_files
    except:
        return []

def extract_fields_from_doc(docs_text: str, client: OpenAI) -> dict:
    """Extract deal fields from documents using LLM."""
    if not docs_text.strip():
        return None
    
    system = """You are a VC investment analyst. Extract key deal information from the provided document.
Return ONLY valid JSON matching this structure (use null for missing values):
{
    "company": "string or null",
    "stage": "Pre-Seed|Seed|Series A|Series B+|null",
    "sector": "string or null",
    "raise_amount_usd": "number or null",
    "arr_usd": "number or null",
    "growth_rate_pct": "number or null",
    "runway_months": "number or null",
    "notes": "string or null"
}"""
    
    user = f"Extract deal info from this document:\n\n{docs_text[:8000]}"
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
        )
        
        response_text = resp.choices[0].message.content.strip()
        # Extract JSON if it's wrapped in markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    except:
        return None

def extract_contact_info(doc_text: str, client: OpenAI) -> str:
    """Extract founder/contact email from deck."""
    try:
        user = f"""Extract the founder or primary contact email address from this pitch deck.
Return ONLY the email address, nothing else. If no email found, return 'not_found'.

Document:
{doc_text[:3000]}"""
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user}],
            temperature=0.0,
        )
        
        email = resp.choices[0].message.content.strip()
        # Basic validation
        if "@" in email and "." in email and "not_found" not in email.lower():
            return email
        return None
    except:
        return None

def mock_scorecard(deal: dict, investor_prefs: dict = None) -> dict:
    """Generate mock scorecard with reasoning."""
    base = 0.62
    reasoning = []
    
    # Safely handle None values
    stage = deal.get("stage") or "Seed"
    growth = deal.get("growth_rate_pct") or 0
    runway = deal.get("runway_months") or 12
    arr = deal.get("arr_usd") or 0
    sector = deal.get("sector") or "Unknown"
    
    if stage in ["Seed", "Pre-Seed"]:
        base -= 0.05
        reasoning.append("Adjustment: Early stage companies carry execution risk")
    if growth >= 15:
        base += 0.08
        reasoning.append(f"Boost: Strong growth rate ({growth}% is solid)")
    if runway < 9:
        base -= 0.07
        reasoning.append("Concern: Short runway (<9 months) increases execution pressure")
    if arr >= 1_000_000:
        base += 0.06
        reasoning.append("Positive: Significant ARR indicates market traction")
    
    if investor_prefs:
        if investor_prefs.get("preferred_stage") == stage:
            base += 0.05
            reasoning.append(f"Match: This aligns with your preferred stage ({stage})")
        if investor_prefs.get("preferred_sector") and investor_prefs["preferred_sector"].lower() in sector.lower():
            base += 0.05
            reasoning.append(f"Sector match: This deal is in {sector}, which matches your focus")
        if investor_prefs.get("min_arr") and arr >= investor_prefs["min_arr"]:
            base += 0.03
            reasoning.append(f"Revenue threshold: Exceeds your minimum ARR target")

    prob = max(0.05, min(0.95, base))
    
    # Detailed drivers with explanations
    drivers_pos_detailed = [
        {
            "title": "Strong growth trajectory",
            "explanation": f"Company shows {growth}% growth rate, which is above market benchmarks for {stage} companies. This indicates strong product-market fit and demand.",
            "impact": "+8% to probability score",
            "source": "Extracted from deal metrics (growth_rate_pct field)"
        },
        {
            "title": "Clear market opportunity",
            "explanation": f"Operating in {sector}, a high-growth sector with expanding TAM. Market timing appears favorable based on industry trends.",
            "impact": "+5% to probability score",
            "source": "Sector analysis and deal documentation"
        },
        {
            "title": "Experienced team",
            "explanation": "Founding team has relevant domain expertise and prior startup experience, reducing execution risk.",
            "impact": "+4% to probability score",
            "source": "Team background (if provided in deck)"
        }
    ]
    
    drivers_neg_detailed = [
        {
            "title": "Competitive market",
            "explanation": f"{sector} is a crowded space with established players. Differentiation and defensibility need to be proven.",
            "impact": "-3% to probability score",
            "source": "Market landscape analysis"
        },
        {
            "title": "Limited runway",
            "explanation": f"With {runway} months of runway, the company needs to hit milestones quickly or raise again soon, increasing execution pressure.",
            "impact": "-7% to probability score" if runway < 9 else "-2% to probability score",
            "source": "Financial metrics (runway_months field)"
        },
        {
            "title": "Team background needs verification",
            "explanation": "Founding team's prior exits and relevant experience not fully documented in available materials.",
            "impact": "-2% to probability score",
            "source": "Missing information in pitch deck"
        }
    ]
    
    # Red flags and missing info combined
    red_flags_detailed = []
    if arr > 0:
        red_flags_detailed.extend([
            {
                "title": "Retention metrics not provided",
                "explanation": "Customer retention rate (NRR/GRR) is critical for SaaS valuations but not disclosed. Without this, we can't assess revenue sustainability.",
                "risk_level": "Medium",
                "source": "Missing from financial documentation"
            },
            {
                "title": "CAC not provided",
                "explanation": "Customer Acquisition Cost is missing. This makes it impossible to validate unit economics and payback periods.",
                "risk_level": "Medium",
                "source": "Missing from pitch deck and financials"
            }
        ])
    else:
        red_flags_detailed.append({
            "title": "No revenue metric provided",
            "explanation": "Company has not disclosed ARR or MRR. This is a red flag for monetization readiness and go-to-market validation.",
            "risk_level": "High",
            "source": "Missing from all deal documents"
        })
    
    if runway < 6:
        red_flags_detailed.append({
            "title": "Critical runway risk",
            "explanation": f"With only {runway} months of cash remaining, the company is in a high-pressure situation that could force unfavorable terms.",
            "risk_level": "High",
            "source": "Financial metrics (runway_months field)"
        })
    
    return {
        "prob_next_round": prob,
        "confidence": 0.72,
        "drivers_pos": [d["title"] for d in drivers_pos_detailed],
        "drivers_pos_detailed": drivers_pos_detailed,
        "drivers_neg": [d["title"] for d in drivers_neg_detailed],
        "drivers_neg_detailed": drivers_neg_detailed,
        "risk_flags": [d["title"] for d in red_flags_detailed],
        "risk_flags_detailed": red_flags_detailed,
        "reasoning": reasoning,
    }

def calculate_category_scores(deal: dict, investor_prefs: dict = None) -> dict:
    """Calculate 0-10 scores for each investment category."""
    scores = {}
    personalization_applied = []
    
    # Market (0-10)
    market_score = 5.0
    sector = deal.get("sector", "").lower()
    growth = deal.get("growth_rate_pct", 0)
    if "ai" in sector or "saas" in sector or "fintech" in sector:
        market_score += 2
    if growth >= 100:
        market_score += 2
    elif growth >= 50:
        market_score += 1
    scores["Market"] = min(10, market_score)
    
    # Team (0-10) - placeholder, would need team data
    team_score = 6.0
    scores["Team"] = team_score
    
    # Traction (0-10)
    traction_score = 0.0
    arr = deal.get("arr_usd", 0)
    if arr >= 5_000_000:
        traction_score = 10
    elif arr >= 1_000_000:
        traction_score = 8
    elif arr >= 500_000:
        traction_score = 6
    elif arr >= 100_000:
        traction_score = 4
    elif arr > 0:
        traction_score = 2
    if growth >= 100:
        traction_score = min(10, traction_score + 2)
    scores["Traction"] = traction_score
    
    # Unit Economics (0-10)
    unit_econ_score = 4.0  # Low because missing CAC, LTV, etc.
    scores["Unit Economics"] = unit_econ_score
    
    # Moat (0-10)
    moat_score = 5.0
    if "platform" in sector or "network" in sector:
        moat_score += 2
    if arr >= 1_000_000:  # Some proof of stickiness
        moat_score += 1
    scores["Moat"] = min(10, moat_score)
    
    # Fund Fit (0-10) - PERSONALIZED based on investor preferences
    fund_fit_score = 5.0
    
    if investor_prefs:
        # Check stage match
        pref_stage = investor_prefs.get("preferred_stage")
        deal_stage = deal.get("stage")
        if pref_stage and deal_stage:
            if pref_stage == deal_stage:
                fund_fit_score += 2
                personalization_applied.append(f"Stage match: {deal_stage} aligns with your focus")
            else:
                fund_fit_score -= 2
                personalization_applied.append(f"Stage mismatch: {deal_stage} vs your preferred {pref_stage}")
        
        # Check sector match
        pref_sector = investor_prefs.get("preferred_sector", "").lower()
        if pref_sector and sector:
            if pref_sector in sector or sector in pref_sector:
                fund_fit_score += 2
                personalization_applied.append(f"Sector match: {sector}")
            else:
                fund_fit_score -= 1
                personalization_applied.append(f"Sector mismatch: {sector} vs your preferred {pref_sector}")
        
        # Check minimum ARR threshold
        min_arr = investor_prefs.get("min_arr", 0)
        if min_arr > 0:
            if arr >= min_arr:
                fund_fit_score += 1
                personalization_applied.append(f"ARR exceeds your ${min_arr:,} minimum")
            elif arr < min_arr and arr > 0:
                fund_fit_score -= 1
                personalization_applied.append(f"ARR below your ${min_arr:,} minimum")
        
        # Check red flags from investor preferences
        red_flags_text = investor_prefs.get("red_flags", "").lower()
        if red_flags_text:
            deal_text = f"{sector} {deal.get('company', '')}".lower()
            if any(flag in deal_text for flag in red_flags_text.split(",")):
                fund_fit_score -= 1
                personalization_applied.append("Red flag keyword match found in preferences")
    
    scores["Fund Fit"] = max(0, min(10, fund_fit_score))
    
    return scores, personalization_applied

def check_missing_metrics(deal: dict) -> dict:
    """Check which key metrics are missing."""
    metrics = {
        "Retention (NRR/GRR)": False,
        "CAC": False,
        "Gross Margin": False,
        "LTV": False,
        "Churn": False,
        "Payback Period": False,
        "Cohort Analysis": False,
        "Pricing Model": False,
    }
    
    # Check for available metrics (would parse from documents in real version)
    arr = deal.get("arr_usd", 0)
    if arr > 0:
        # If they have revenue, assume they might have pricing
        metrics["Pricing Model"] = True
    
    return metrics

def get_investment_decision(prob: float) -> tuple:
    """Return decision and emoji based on probability."""
    if prob >= 0.75:
        return "Proceed", "✅"
    elif prob >= 0.55:
        return "Watch", "🟡"
    else:
        return "Pass", "❌"

def compute_thesis_fit(deal: dict, investor_prefs: dict) -> dict:
    """Compute thesis fit score."""
    if not investor_prefs:
        return None
    
    score = 50
    
    # Safely handle None
    stage = deal.get("stage") or "Unknown"
    sector = deal.get("sector") or "Unknown"
    arr = deal.get("arr_usd") or 0
    runway = deal.get("runway_months") or 12
    
    if investor_prefs.get("preferred_stage") == stage:
        score += 20
    if investor_prefs.get("preferred_sector") and investor_prefs["preferred_sector"].lower() in sector.lower():
        score += 20
    if investor_prefs.get("min_arr") and arr >= investor_prefs["min_arr"]:
        score += 10
    if runway < 6:
        score -= 15
    
    score = max(0, min(100, score))
    
    return {"score": score}

def generate_recommendation(prob: float, thesis_fit: dict = None) -> dict:
    """Generate VC recommendation."""
    combined = prob * 0.6 + (thesis_fit["score"] / 100 * 0.4) if thesis_fit else prob
    
    if combined >= 0.70:
        rec = "INVEST"
        conf = "High"
    elif combined >= 0.50:
        rec = "WATCHLIST"
        conf = "Medium"
    else:
        rec = "PASS"
        conf = "Low"
    
    return {"recommendation": rec, "confidence": conf}

def generate_founder_questions(deal: dict, client: OpenAI) -> str:
    """Generate questions to ask founder."""
    try:
        user = f"""Generate 8-10 diligence questions for a founder of:
Company: {deal.get('company', 'Unknown')}
Stage: {deal.get('stage', 'Unknown')}
Growth: {deal.get('growth_rate_pct', 0)}%
ARR: ${deal.get('arr_usd', 0):,}

Make questions specific, insightful, and operator-friendly."""
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Could not generate questions."

def generate_ic_memo(deal: dict, result: dict, client: OpenAI) -> str:
    """Generate IC memo."""
    try:
        user = f"""Write a concise IC memo (2-3 sentences per section) for:
Company: {deal.get('company')}
Stage: {deal.get('stage')}
Raise: ${deal.get('raise_amount_usd', 0):,}
ARR: ${deal.get('arr_usd', 0):,}
Growth: {deal.get('growth_rate_pct', 0)}%

Sections: Overview | Stage & Market | Traction | Risks | Investment Thesis | Recommendation"""
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user}],
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Could not generate memo."

def generate_founder_followup(deal: dict, result: dict, missing_metrics: dict, client: OpenAI) -> str:
    """Generate friendly founder follow-up email."""
    try:
        # Extract missing metrics and top risks
        missing_list = [metric for metric, available in missing_metrics.items() if not available]
        top_risks = result.get('drivers_neg_detailed', [])[:3]
        red_flags = result.get('risk_flags_detailed', [])
        
        missing_str = ", ".join(missing_list[:5]) if missing_list else "None"
        risks_str = ", ".join([r['title'] for r in top_risks])
        flags_str = ", ".join([f['title'] for f in red_flags[:3]])
        
        user = f"""Generate a warm, professional follow-up email to the founder of {deal.get('company', 'the company')}.

Context:
- Stage: {deal.get('stage')}
- ARR: ${deal.get('arr_usd', 0):,}
- Growth: {deal.get('growth_rate_pct', 0)}%
- Missing metrics: {missing_str}
- Top risk areas: {risks_str}
- Red flags/missing info: {flags_str}

Email should:
1. Short friendly intro (1-2 sentences) - we're interested and doing diligence
2. Bulleted list of 4-6 specific questions about missing metrics and risk areas
3. Request for data room access or KPI definitions document
4. Warm, collaborative close

Tone: Professional but friendly, like a helpful partner. Keep it concise (under 200 words).
Format: Ready to copy-paste."""
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate follow-up email: {str(e)}"

def refine_content(original_content: str, refinement_request: str, content_type: str, client: OpenAI) -> str:
    """Refine generated content based on user feedback."""
    try:
        content_labels = {
            "questions": "founder diligence questions",
            "email": "founder follow-up email",
            "memo": "IC memo"
        }
        
        user = f"""You previously generated this {content_labels.get(content_type, 'content')}:

{original_content}

The user requests the following changes:
{refinement_request}

Please provide the updated version incorporating their feedback. Maintain the same format and tone, but apply the requested changes."""
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user}],
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not refine content: {str(e)}"

def reset_deal():
    """Reset all deal fields safely."""
    for k in ["company", "stage", "sector", "raise_amount_usd", "arr_usd", "growth_rate_pct", "runway_months", "notes"]:
        st.session_state[k] = None
    st.session_state.last_deal = None
    st.session_state.last_result = None
    st.session_state.extracted = None
    st.session_state.docs_text = ""
    st.session_state.extracted_highlights = None
    st.session_state.founder_questions = None
    st.session_state.founder_followup = None
    st.session_state.founder_email = None
    st.session_state.ic_memo = None
    st.toast("✨ Deal reset")

def get_progress_status():
    """Return progress indicators."""
    docs_uploaded = bool(st.session_state.docs_text)
    fields_filled = all(st.session_state.get(k) for k in ["company", "stage", "sector", "raise_amount_usd"])
    analysis_ready = bool(st.session_state.last_result)
    
    return docs_uploaded, fields_filled, analysis_ready

# ========================================
# MAIN PAGE HEADER
# ========================================
col_title, col_actions = st.columns([1, 0.35])
with col_title:
    # Breadcrumb
    _company_bc = st.session_state.get("company") or "New Deal"
    _list_bc = st.session_state.get("active_list", "active").capitalize()
    # Show analysis badge if result exists
    _badge_html = ""
    if st.session_state.get("last_result"):
        _r = st.session_state.last_result
        _p = _r.get("prob_next_round", 0)
        _dec_raw, _ = get_investment_decision(_p)
        _badge_cls = {"Proceed": "badge-proceed", "Watch": "badge-watch", "Pass": "badge-pass"}.get(_dec_raw, "badge-watch")
        _badge_html = f'<span class="{_badge_cls}" style="margin-left:12px;">● {_dec_raw.upper()} · {_p:.0%}</span>'
    st.markdown(f"""
    <div class="vc-breadcrumb">
        <span class="crumb">Deals</span>
        <span class="sep">/</span>
        <span class="crumb">{_list_bc}</span>
        <span class="sep">/</span>
        <span class="current">{_company_bc}</span>
        {_badge_html}
    </div>
    """, unsafe_allow_html=True)

with col_actions:
    col_exp, col_reset = st.columns(2)
    with col_exp:
        if st.button("↓ Export", use_container_width=True, help="Export deal data"):
            st.toast("Export coming soon!")
    with col_reset:
        if st.button("+ New Deal", use_container_width=True, type="primary", help="Clear all fields and start fresh"):
            reset_deal()
            st.rerun()

# ========================================
# SIDEBAR: AUTHENTICATION & INVESTOR PROFILE
# ========================================
with st.sidebar:
    # Brand header
    st.markdown("""
    <div style="padding:0.5rem 0 1.25rem;">
        <div style="font-size:1.1em;font-weight:800;color:#f1f5f9;letter-spacing:-0.02em;">VCaaS</div>
        <div style="font-size:0.72em;color:#3a4a65;margin-top:2px;">Deal Intake & Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    # Authentication section
    if not st.session_state.logged_in:
        st.markdown('<div style="font-size:0.68em;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#3a4a65;margin-bottom:0.75rem;">Sign In</div>', unsafe_allow_html=True)
        
        auth_tab = st.radio("", ["Login", "Create Account"], horizontal=True, label_visibility="collapsed")
        
        username_input = st.text_input("Username", key="auth_username")
        password_input = st.text_input("Password", type="password", key="auth_password")
        
        # Show error only if it was set by a button click
        if st.session_state.login_error:
            st.error(st.session_state.login_error)
        
        if auth_tab == "Login":
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if username_input and password_input:
                    if login_user(username_input, password_input):
                        st.success(f"Welcome back, {username_input}!")
                        st.rerun()
                    else:
                        st.session_state.login_error = "Invalid username or password"
                        st.rerun()
                else:
                    st.session_state.login_error = "Please enter username and password"
                    st.rerun()
        else:
            if st.button("✨ Create Account", use_container_width=True, type="primary"):
                if username_input and password_input:
                    if signup_user(username_input, password_input):
                        st.success(f"Account created! Welcome, {username_input}!")
                        st.rerun()
                    else:
                        st.session_state.login_error = "Username already exists"
                        st.rerun()
                else:
                    st.session_state.login_error = "Please provide username and password"
                    st.rerun()
        
        st.divider()
        st.caption("Your preferences and history will be saved to your account")
        st.caption("💡 Tip: Stay logged in across page reloads")
    
    else:
        # User is logged in
        _uname = st.session_state.current_user
        _initials = _uname[:2].upper()
        col_usr, col_out = st.columns([3, 1])
        with col_usr:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:9px;padding:0.4rem 0;">
                <div style="width:30px;height:30px;border-radius:50%;background:#2563eb;display:flex;align-items:center;justify-content:center;font-size:0.72em;font-weight:700;color:white;flex-shrink:0;">{_initials}</div>
                <span style="font-size:0.88em;font-weight:600;color:#e2e8f0;">{_uname}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_out:
            if st.button("Out", key="logout_btn", help="Logout"):
                logout_user()
                st.rerun()

        st.markdown('<div style="border-top:1px solid #1a2540;margin:0.75rem 0;"></div>', unsafe_allow_html=True)

    # Investor Profile section (only shown when logged in)
    if st.session_state.logged_in:
        col_pref, col_toggle = st.columns([3, 1])
        with col_pref:
            st.markdown('<div style="font-size:0.68em;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#3a4a65;">Investor Profile</div>', unsafe_allow_html=True)
        with col_toggle:
            if st.button("Edit", help="Edit preferences", key="edit_prefs"):
                st.session_state.show_prefs_onboard = not st.session_state.show_prefs_onboard
                st.rerun()

    if st.session_state.investor_prefs:
        _ip = st.session_state.investor_prefs
        st.markdown(f"""
        <div style="background:#131929;border:1px solid #1e2a40;border-radius:10px;padding:10px 13px;margin-bottom:0.75rem;">
            <div style="font-size:0.82em;color:#e2e8f0;font-weight:600;margin-bottom:4px;">{_ip.get('investor_name','—')}</div>
            <div style="font-size:0.75em;color:#3a4a65;">{_ip.get('preferred_stage','Any')} · {_ip.get('preferred_sector','Any sector')}</div>
            <div style="font-size:0.72em;color:#3a4a65;margin-top:2px;">Min ARR ${_ip.get('min_arr',0):,}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👉 Set up your investor profile to personalize deal scoring.")
    
    st.divider()
    
    # Investor preferences form (modal-like in sidebar)
    if st.session_state.show_prefs_onboard:
        st.markdown("### 🎯 Edit Your Profile")
        
        investor_name = st.text_input(
            "Your name / Fund name",
            value=st.session_state.investor_prefs.get("investor_name", "") if st.session_state.investor_prefs else "",
            placeholder="e.g., John Smith, Acme VC"
        )
        
        preferred_stage = st.selectbox(
            "Primary stage",
            ["Any", "Pre-Seed", "Seed", "Series A", "Series B+"],
            index=0
        )
        
        preferred_sector = st.text_input(
            "Preferred sector(s)",
            value=st.session_state.investor_prefs.get("preferred_sector", "") if st.session_state.investor_prefs else "",
            placeholder="e.g., B2B SaaS, AI"
        )
        
        min_arr = st.number_input(
            "Minimum ARR ($)",
            min_value=0,
            step=100000,
            value=st.session_state.investor_prefs.get("min_arr", 0) if st.session_state.investor_prefs else 0
        )
        
        ethos = st.text_area(
            "Investment ethos",
            value=st.session_state.investor_prefs.get("ethos", "") if st.session_state.investor_prefs else "",
            placeholder="What do you look for?",
            height=60
        )
        
        red_flags = st.text_area(
            "Red flag keywords (comma-separated)",
            value=st.session_state.investor_prefs.get("red_flags", "") if st.session_state.investor_prefs else "",
            placeholder="e.g., crypto, gambling, tobacco",
            height=50
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", use_container_width=True, type="primary"):
                prefs = {
                    "investor_name": investor_name,
                    "preferred_stage": preferred_stage if preferred_stage != "Any" else None,
                    "preferred_sector": preferred_sector,
                    "min_arr": min_arr,
                    "ethos": ethos,
                    "red_flags": red_flags,
                }
                st.session_state.investor_prefs = prefs
                # Save to user account if logged in
                if st.session_state.logged_in:
                    save_user_preferences(prefs)
                st.session_state.show_prefs_onboard = False
                st.success("✅ Profile saved!")
                st.rerun()
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_prefs_onboard = False
                st.rerun()
        
        st.divider()
    
    # Deal Pipeline section (only shown when logged in)
    if st.session_state.logged_in:
        st.markdown('<div style="font-size:0.68em;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#3a4a65;margin-bottom:0.75rem;">Pipeline</div>', unsafe_allow_html=True)

        # Counts
        wl_n = len([d for d in st.session_state.saved_deals if d.get("status") == "watchlist"])
        ac_n = len([d for d in st.session_state.saved_deals if d.get("status") == "active"])
        rv_n = len([d for d in st.session_state.saved_deals if d.get("status") == "reviewed"])
        ps_n = len([d for d in st.session_state.saved_deals if d.get("status") == "passed"])

        # 2x2 metric grid
        st.markdown(f"""
        <div class="pl-metrics">
            <div class="pl-metric"><div class="pl-num">{wl_n}</div><div class="pl-lbl">Watchlist</div></div>
            <div class="pl-metric"><div class="pl-num" style="color:#60a5fa;">{ac_n}</div><div class="pl-lbl">Active</div></div>
            <div class="pl-metric"><div class="pl-num">{rv_n}</div><div class="pl-lbl">Reviewed</div></div>
            <div class="pl-metric"><div class="pl-num" style="color:#475569;">{ps_n}</div><div class="pl-lbl">Passed</div></div>
        </div>
        """, unsafe_allow_html=True)

        # List selector
        list_tabs = st.segmented_control(
            "Select List",
            options=["watchlist", "active", "reviewed", "passed"],
            format_func=lambda x: {"watchlist": "Watch", "active": "Active", "reviewed": "Review", "passed": "Pass"}[x],
            default=st.session_state.active_list,
            label_visibility="collapsed"
        )
        if list_tabs:
            st.session_state.active_list = list_tabs

        # Search
        search_filter = st.text_input(
            "Search",
            value=st.session_state.deal_filters["search"],
            placeholder="Search deals…",
            label_visibility="collapsed",
            key="sidebar_search"
        )
        st.session_state.deal_filters["search"] = search_filter

        # Filters expander
        with st.expander("Filters", expanded=False):
            all_stages = ["Pre-Seed", "Seed", "Series A", "Series B+"]
            stage_filter = st.multiselect("Stage", options=all_stages, default=st.session_state.deal_filters["stages"])
            st.session_state.deal_filters["stages"] = stage_filter

            all_sectors = list(set([d.get("sector") for d in st.session_state.saved_deals if d.get("sector")]))
            sector_filter = st.multiselect("Sector", options=sorted(all_sectors), default=[s for s in st.session_state.deal_filters["sectors"] if s in all_sectors])
            st.session_state.deal_filters["sectors"] = sector_filter

            decision_filter = st.multiselect("Decision", options=["Proceed", "Watch", "Pass"], default=st.session_state.deal_filters["decisions"])
            st.session_state.deal_filters["decisions"] = decision_filter

            sort_filter = st.selectbox("Sort", options=["last_updated", "probability", "arr"],
                format_func=lambda x: {"last_updated": "Last Updated", "probability": "Probability ↓", "arr": "ARR ↓"}[x],
                index=["last_updated", "probability", "arr"].index(st.session_state.deal_filters["sort_by"]))
            st.session_state.deal_filters["sort_by"] = sort_filter

            if st.button("Reset Filters", use_container_width=True):
                st.session_state.deal_filters = {"stages": [], "sectors": [], "decisions": [], "min_arr": 0, "search": "", "sort_by": "last_updated"}
                st.rerun()

        st.markdown('<div style="border-top:1px solid #1a2540;margin:0.75rem 0;"></div>', unsafe_allow_html=True)

        # Deal list
        filtered_deals = get_filtered_deals(st.session_state.active_list)
        st.markdown(f'<div style="font-size:0.72em;color:#3a4a65;margin-bottom:0.5rem;">{len(filtered_deals)} deals in {st.session_state.active_list.capitalize()}</div>', unsafe_allow_html=True)

        if filtered_deals:
            for _deal in filtered_deals[:20]:
                _dc = {"Proceed": "#10b981", "Watch": "#f59e0b", "Pass": "#ef4444"}.get(_deal.get("decision"), "#475569")
                _pct = f"{_deal.get('prob_next_round', 0):.0%}"
                _is_active = (_deal.get("company") == (st.session_state.get("company") or ""))
                _border = "#3b82f6" if _is_active else "#1e2a40"
                _bg = "rgba(59,130,246,0.06)" if _is_active else "#131929"

                st.markdown(f"""
                <div style="background:{_bg};border:1px solid {_border};border-radius:10px;padding:9px 11px;margin-bottom:5px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.88em;font-weight:600;color:#e2e8f0;">{_deal['company']}</span>
                        <span style="font-size:0.8em;font-weight:700;color:{_dc};">{_pct}</span>
                    </div>
                    <div style="font-size:0.72em;color:#3a4a65;margin-top:3px;">{_deal.get('stage','—')} · {_deal.get('sector','')[:22]}</div>
                </div>
                """, unsafe_allow_html=True)

                load_col, move_col = st.columns([3, 2])
                with load_col:
                    if st.button("Open →", key=f"load_{_deal['id']}", use_container_width=True):
                        load_deal(_deal)
                        st.session_state.active_tab = "Analysis"
                        st.toast(f"Loaded {_deal['company']}")
                        st.rerun()
                with move_col:
                    new_status = st.selectbox(
                        "Move",
                        options=["watchlist", "active", "reviewed", "passed"],
                        index=["watchlist", "active", "reviewed", "passed"].index(_deal.get("status", "watchlist")),
                        format_func=lambda x: {"watchlist": "📌", "active": "⚡", "reviewed": "📋", "passed": "❌"}[x],
                        key=f"status_{_deal['id']}",
                        label_visibility="collapsed"
                    )
                    if new_status != _deal.get("status"):
                        update_deal_status(_deal["id"], new_status)
                        st.rerun()
        else:
            st.markdown(f'<div style="font-size:0.85em;color:#3a4a65;padding:1rem 0;text-align:center;">No deals in {st.session_state.active_list.capitalize()}</div>', unsafe_allow_html=True)

    elif st.session_state.logged_in:
        st.markdown('<div style="font-size:0.68em;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#3a4a65;margin-bottom:0.75rem;">Pipeline</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.85em;color:#3a4a65;text-align:center;padding:1rem 0;">No saved deals yet. Run analysis and save your first deal!</div>', unsafe_allow_html=True)

# ========================================
# PROGRESS STEPPER + TABS (combined)
# ========================================
docs_up, fields_filled, analysis_done = get_progress_status()

def _step(done, label):
    color = "#10b981" if done else "#2a3550"
    txt_color = "#34d399" if done else "#3a4a65"
    tick = "✓" if done else "·"
    return f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:0.78em;color:{txt_color};font-weight:600;"><span style="width:16px;height:16px;border-radius:50%;background:{color}20;border:1.5px solid {color};display:inline-flex;align-items:center;justify-content:center;font-size:0.7em;">{tick}</span>{label}</span>'

steps_html = f"""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:1.25rem;flex-wrap:wrap;">
    {_step(docs_up, "Docs Uploaded")}
    <span style="color:#1e2a40;font-size:0.75em;">──</span>
    {_step(bool(st.session_state.extracted), "Fields Extracted")}
    <span style="color:#1e2a40;font-size:0.75em;">──</span>
    {_step(fields_filled, "Fields Filled")}
    <span style="color:#1e2a40;font-size:0.75em;">──</span>
    {_step(analysis_done, "Analyzed")}
</div>
"""
st.markdown(steps_html, unsafe_allow_html=True)

# Tab navigation
_t = st.session_state.active_tab
tab_col1, tab_col2, tab_col3, spacer = st.columns([1, 1, 1, 4])
with tab_col1:
    if st.button("📥  Intake", use_container_width=True, type="primary" if _t == "Intake" else "secondary"):
        scroll_to_top(); st.session_state.active_tab = "Intake"; st.rerun()
with tab_col2:
    if st.button("📊  Analysis", use_container_width=True, type="primary" if _t == "Analysis" else "secondary"):
        scroll_to_top(); st.session_state.active_tab = "Analysis"; st.rerun()
with tab_col3:
    if st.button("💬  Copilot", use_container_width=True, type="primary" if _t == "Copilot" else "secondary"):
        scroll_to_top(); st.session_state.active_tab = "Copilot"; st.rerun()

st.markdown('<div style="border-bottom:1px solid #1e2a40;margin:0.5rem 0 1.5rem;"></div>', unsafe_allow_html=True)

# ========================================
# TAB CONTENT
# ========================================

# Require login to access main content
if not st.session_state.logged_in:
    st.info("👈 Please login or create an account to access the deal analysis platform")
    st.stop()

# Show content based on active_tab
if st.session_state.active_tab == "Intake":
    st.markdown('<div class="form-section-title">📄 Documents & Data</div>', unsafe_allow_html=True)
    
    # Document upload
    with st.form("doc_upload_form"):
        st.markdown("**Upload your deal documents** — Extract key details automatically")
        st.caption("💡 Max file size: 50MB per file. For larger files, try compressing the PDF or splitting documents.")
        
        st.markdown("**Pitch Deck** — Primary source for deal info (PDF, PPTX, or ZIP)")
        deck = st.file_uploader("Pitch Deck (PDF/PPTX/ZIP)", type=["pdf", "pptx", "zip"], label_visibility="collapsed", key="deck")
        
        st.markdown("**Additional Materials** — Supporting docs, one-pagers, whitepapers (optional)")
        extra = st.file_uploader("Additional Documents (PDF, PPTX, TXT, ZIP)", type=["pdf", "pptx", "txt", "zip"], accept_multiple_files=True, label_visibility="collapsed", key="extra")
        
        st.markdown("**Financials** — Spreadsheets with metrics, projections (optional)")
        financials = st.file_uploader("Financials (CSV/XLSX)", type=["csv", "xlsx"], label_visibility="collapsed", key="fin")
        
        st.divider()
        
        st.markdown("**Additional Context** — Background info not in documents (optional)")
        notes_input = st.text_area(
            "Notes",
            value=st.session_state.notes or "",
            height=80,
            placeholder="Founder email, diligence notes, meeting summary, red flags, etc.",
            label_visibility="collapsed"
        )
        st.session_state.notes = notes_input if notes_input.strip() else None
        
        st.divider()
        
        col_extract, col_preview = st.columns(2)
        with col_extract:
            extract_btn = st.form_submit_button("🔍 Extract Fields from Docs", use_container_width=True)
        
        with col_preview:
            if st.session_state.docs_text:
                preview_len = len(st.session_state.docs_text)
                st.metric("Documents Loaded", f"{preview_len:,} chars", label_visibility="collapsed")
        
        if extract_btn:
            # Validate file sizes (50MB = 50 * 1024 * 1024 bytes)
            max_size = 50 * 1024 * 1024
            oversized_files = []
            
            if deck and deck.size > max_size:
                oversized_files.append(f"{deck.name} ({deck.size / (1024*1024):.1f}MB)")
            
            if extra:
                for f in extra:
                    if f.size > max_size:
                        oversized_files.append(f"{f.name} ({f.size / (1024*1024):.1f}MB)")
            
            if financials and financials.size > max_size:
                oversized_files.append(f"{financials.name} ({financials.size / (1024*1024):.1f}MB)")
            
            if oversized_files:
                st.error(f"⚠️ **Files too large (max 50MB):**\n\n" + "\n".join([f"• {f}" for f in oversized_files]))
                st.info("💡 **Tips to reduce file size:**\n- Compress PDF using online tools (ilovepdf.com, smallpdf.com)\n- Save PowerPoint as PDF with lower quality images\n- Remove high-res images or unnecessary slides\n- Split large documents into smaller files")
                st.stop()
            
            # Process documents
            docs_parts = []
            
            if deck:
                if deck.name.endswith(".pdf"):
                    docs_parts.append(pdf_to_text(deck))
                elif deck.name.endswith(".pptx"):
                    docs_parts.append(pptx_to_text(deck))
                elif deck.name.endswith(".zip"):
                    extracted = extract_zip(deck)
                    for filename, file_obj in extracted:
                        if filename.endswith(".pdf"):
                            docs_parts.append(pdf_to_text(file_obj))
                        elif filename.endswith(".pptx"):
                            docs_parts.append(pptx_to_text(file_obj))
                        elif filename.endswith(".txt"):
                            docs_parts.append(txt_to_text(file_obj))
            
            if extra:
                for f in extra:
                    if f.name.endswith(".pdf"):
                        docs_parts.append(pdf_to_text(f))
                    elif f.name.endswith(".pptx"):
                        docs_parts.append(pptx_to_text(f))
                    elif f.name.endswith(".txt"):
                        docs_parts.append(txt_to_text(f))
                    elif f.name.endswith(".zip"):
                        extracted = extract_zip(f)
                        for filename, file_obj in extracted:
                            if filename.endswith(".pdf"):
                                docs_parts.append(pdf_to_text(file_obj))
                            elif filename.endswith(".pptx"):
                                docs_parts.append(pptx_to_text(file_obj))
                            elif filename.endswith(".txt"):
                                docs_parts.append(txt_to_text(file_obj))
            
            if financials:
                docs_parts.append(tabular_to_text(financials))
            
            st.session_state.docs_text = "\n".join(docs_parts)
            
            if st.session_state.docs_text:
                client = get_openai_client()
                if client:
                    with st.spinner("🤖 Extracting deal fields..."):
                        st.session_state.extracted = extract_fields_from_doc(st.session_state.docs_text, client)
                        # Also extract contact info
                        st.session_state.founder_email = extract_contact_info(st.session_state.docs_text, client)
                    
                    if st.session_state.extracted:
                        st.success("✅ Extraction successful!")
                        if st.session_state.founder_email:
                            st.info(f"📧 Found contact: {st.session_state.founder_email}")
                    else:
                        st.warning("⚠️ Could not extract fields. Review document quality.")
    
    st.divider()
    
    # Extraction preview
    if st.session_state.extracted:
        st.markdown('<div class="form-section-title">🔍 Extracted Data Preview</div>', unsafe_allow_html=True)
        
        with st.expander("View JSON", expanded=False):
            st.code(json.dumps(st.session_state.extracted, indent=2), language="json")
        
        if st.button("✨ Apply to form", use_container_width=True, type="primary"):
            for k in ["company", "stage", "sector", "raise_amount_usd", "arr_usd", "growth_rate_pct", "runway_months", "notes"]:
                if k in st.session_state.extracted and st.session_state.extracted[k] is not None:
                    st.session_state[k] = st.session_state.extracted[k]
            st.success("✓ Fields applied!")
            st.rerun()
    
    st.divider()
    
    # Deal fields
    st.markdown('<div class="form-section-title">📋 Deal Details</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**Company & Sector**")
        company_input = st.text_input(
            "Company name",
            value=st.session_state.company or "",
            placeholder="e.g., TechCorp AI"
        )
        st.session_state.company = company_input if company_input else None
        
        sector_input = st.text_input(
            "Sector",
            value=st.session_state.sector or "",
            placeholder="e.g., B2B SaaS, AI, Climate Tech"
        )
        st.session_state.sector = sector_input if sector_input else None
    
    with col2:
        st.markdown("**Funding**")
        stage_opts = ["Pre-Seed", "Seed", "Series A", "Series B+"]
        stage_idx = stage_opts.index(st.session_state.stage) if st.session_state.stage in stage_opts else 0
        stage_select = st.selectbox(
            "Stage",
            stage_opts,
            index=stage_idx
        )
        st.session_state.stage = stage_select
        
        raise_input = st.number_input(
            "Raise amount ($)",
            min_value=0,
            step=250000,
            value=st.session_state.raise_amount_usd or 0,
            format="%d"
        )
        st.session_state.raise_amount_usd = raise_input if raise_input > 0 else None
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("**Traction**")
        arr_input = st.number_input(
            "ARR ($)",
            min_value=0,
            step=100000,
            value=st.session_state.arr_usd or 0,
            format="%d"
        )
        st.session_state.arr_usd = arr_input if arr_input > 0 else None
        
        growth_input = st.number_input(
            "Growth rate (%)",
            min_value=0,
            max_value=500,
            step=1,
            value=st.session_state.growth_rate_pct or 0
        )
        st.session_state.growth_rate_pct = growth_input if growth_input > 0 else None
    
    with col2:
        st.markdown("**Health**")
        runway_input = st.number_input(
            "Runway (months)",
            min_value=0,
            max_value=60,
            step=1,
            value=st.session_state.runway_months or 0
        )
        st.session_state.runway_months = runway_input if runway_input > 0 else None
    
    st.divider()
    
    # Validation warnings
    validation_issues = []
    if not st.session_state.get("company"):
        validation_issues.append("Company name is required")
    if not st.session_state.get("stage"):
        validation_issues.append("Investment stage is required")
    if not st.session_state.get("sector"):
        validation_issues.append("Sector is required")
    
    if validation_issues:
        st.markdown(f"""
        <div class="warning-box">
        ⚠️ <b>Missing required fields:</b><br>
        {chr(10).join(f"• {issue}" for issue in validation_issues)}
        </div>
        """, unsafe_allow_html=True)
    
    # Run analysis button
    col_run, col_empty = st.columns([1, 2])
    with col_run:
        if st.button("▶ Run Analysis", use_container_width=True, type="primary", help="Analyze this deal"):
            if not validation_issues:
                deal = {
                    "company": st.session_state.company,
                    "stage": st.session_state.stage,
                    "sector": st.session_state.sector,
                    "raise_amount_usd": st.session_state.raise_amount_usd or 0,
                    "arr_usd": st.session_state.arr_usd or 0,
                    "growth_rate_pct": st.session_state.growth_rate_pct or 0,
                    "runway_months": st.session_state.runway_months or 0,
                    "notes": st.session_state.notes or "",
                }
                
                st.session_state.last_deal = deal
                st.session_state.last_result = mock_scorecard(deal, st.session_state.investor_prefs)
                st.session_state.extracted_highlights = None
                st.session_state.founder_questions = None
                st.session_state.founder_followup = None
                st.session_state.ic_memo = None
                
                # Switch to Analysis tab
                st.session_state.active_tab = "Analysis"
                st.rerun()
                
                st.success("✅ Analysis complete!")
            else:
                st.error("❌ Please fix validation issues above.")

elif st.session_state.active_tab == "Analysis":
    scroll_to_top()
    if not st.session_state.last_result:
        st.markdown("""
        <div class="vc-card" style="text-align:center;padding:3rem 2rem;margin-top:2rem;">
            <div style="font-size:2.5em;margin-bottom:1rem;">📊</div>
            <div style="font-size:1.05em;font-weight:600;color:#e2e8f0;margin-bottom:0.5rem;">No Analysis Yet</div>
            <div style="font-size:0.875em;color:#475569;">Complete deal intake and run analysis to see results here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        deal = st.session_state.last_deal
        result = st.session_state.last_result
        prob = result["prob_next_round"]
        confidence = result.get("confidence", 0.72)

        # Core calculations
        category_scores, personalization_applied = calculate_category_scores(deal, st.session_state.investor_prefs)
        missing_metrics = check_missing_metrics(deal)
        decision, decision_emoji = get_investment_decision(prob)

        missing_count = sum(1 for v in missing_metrics.values() if not v)
        time_to_diligence = 7 + missing_count * 2

        deal_quality = 50
        deal_quality += min(20, prob * 30)
        deal_quality += min(15, (8 - missing_count) * 2)
        deal_quality += min(15, category_scores.get("Fund Fit", 5) * 1.5)
        deal_quality = max(0, min(100, deal_quality))
        fit_score = int(category_scores.get("Fund Fit", 5) * 10)

        arr_val = deal.get('arr_usd', 0) or 0
        raise_val = deal.get('raise_amount_usd', 0) or 0
        growth_pct = deal.get('growth_rate_pct', 0) or 0
        runway = deal.get('runway_months', 0) or 0

        arr_display = f"${arr_val/1_000_000:.1f}M" if arr_val >= 1_000_000 else f"${arr_val/1_000:.0f}K" if arr_val >= 1_000 else f"${arr_val}"
        raise_display = f"${raise_val/1_000_000:.1f}M" if raise_val >= 1_000_000 else f"${raise_val/1_000:.0f}K" if raise_val >= 1_000 else f"${raise_val}"

        # Decision colors
        d_color = {"Proceed": "#10b981", "Watch": "#f59e0b", "Pass": "#ef4444"}[decision]
        d_badge = {"Proceed": "badge-proceed", "Watch": "badge-watch", "Pass": "badge-pass"}[decision]
        fit_color = "#10b981" if fit_score >= 70 else "#f59e0b" if fit_score >= 40 else "#ef4444"
        q_color = "#10b981" if deal_quality >= 70 else "#f59e0b" if deal_quality >= 50 else "#ef4444"
        g_class = "pv-green" if growth_pct > 10 else "pv-red" if growth_pct <= 0 else "pv-orange"
        r_class = "pv-green" if runway >= 18 else "pv-orange" if runway >= 12 else "pv-red"
        stage_class = {"Pre-Seed": "pv-purple", "Seed": "pv-blue", "Series A": "pv-green", "Series B+": "pv-orange"}.get(deal.get("stage", ""), "pv-blue")

        # ── DEAL PILLS ROW ─────────────────────────────────────────────
        st.markdown(f"""
        <div class="pills-row">
            <div class="pill"><span class="pill-lbl">Stage</span><span class="pill-val {stage_class}">{deal.get('stage','—')}</span></div>
            <div class="pill" style="min-width:160px;"><span class="pill-lbl">Sector</span><span class="pill-val" style="font-size:0.8em;">{deal.get('sector','—')}</span></div>
            <div class="pill"><span class="pill-lbl">ARR</span><span class="pill-val pv-green">{arr_display}</span></div>
            <div class="pill"><span class="pill-lbl">Raising</span><span class="pill-val pv-orange">{raise_display}</span></div>
            <div class="pill"><span class="pill-lbl">Runway</span><span class="pill-val {r_class}">{runway} mo</span></div>
            <div class="pill"><span class="pill-lbl">Growth</span><span class="pill-val {g_class}">{growth_pct:.0f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

        # ── PERSONALIZATION NOTICE ──────────────────────────────────────
        if personalization_applied:
            notice_text = " · ".join(personalization_applied)
            st.markdown(f"""
            <div class="pers-notice">
                <span style="margin-top:1px;">⊙</span>
                <span>Personalization active — <strong>{notice_text}</strong></span>
            </div>
            """, unsafe_allow_html=True)

        # ── TWO-COLUMN LAYOUT: main + right panel ─────────────────────
        main_col, right_col = st.columns([11, 5])

        with main_col:
            # ── TOP 3 CARDS ─────────────────────────────────────────────
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f"""
                <div class="vc-card">
                    <div class="vc-card-title">Investment Decision</div>
                    <div class="{d_badge}" style="margin-bottom:1.1rem;display:inline-flex;">● {decision.upper()}</div>
                    <div class="big-score" style="margin-top:0.5rem;">
                        <span class="bs-pct" style="color:{d_color};">{prob:.0%}</span>
                    </div>
                    <div class="bs-sub">next-round probability</div>
                    <div style="border-top:1px solid #141c2e;margin-top:0.75rem;padding-top:0.75rem;display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.75em;color:#3a4a65;">Model confidence</span>
                        <span style="font-size:0.82em;font-weight:700;color:#64748b;">{int(confidence*100)}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                sector_note = "Sector outside thesis" if any("sector" in p.lower() for p in (personalization_applied or [])) else "Sector match"
                st.markdown(f"""
                <div class="vc-card">
                    <div class="vc-card-title">Investor Fit</div>
                    <div class="big-score">
                        <span class="bs-num" style="color:{fit_color};">{fit_score}</span>
                        <span class="bs-denom">/100</span>
                    </div>
                    <div class="bs-sub">{sector_note}</div>
                    <div class="bar-track" style="margin-top:auto;">
                        <div class="bar-fill" style="width:{fit_score}%;background:{fit_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="vc-card">
                    <div class="vc-card-title">Deal Quality</div>
                    <div class="big-score">
                        <span class="bs-num" style="color:{q_color};">{deal_quality:.0f}</span>
                        <span class="bs-denom">/100</span>
                    </div>
                    <div class="bs-sub">{missing_count}/8 key metrics missing · ~{time_to_diligence} days to complete diligence</div>
                    <div class="bar-track">
                        <div class="bar-fill" style="width:{deal_quality}%;background:{q_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── SCORE BREAKDOWN + WHY THIS SCORE ───────────────────────
            sb_col, why_col = st.columns(2)

            with sb_col:
                bars_html = ""
                for cat, score in category_scores.items():
                    pct = score / 10.0 * 100
                    col = "#10b981" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
                    lbl = (cat[:9] + ".") if len(cat) > 10 else cat
                    bars_html += f"""
                    <div class="score-bar-row">
                        <span class="sbl">{lbl}</span>
                        <div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{col};"></div></div>
                        <span class="sbv" style="color:{col};">{score:.1f}</span>
                    </div>"""

                st.markdown(f"""
                <div class="vc-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <span class="vc-card-title" style="margin-bottom:0;">Score Breakdown</span>
                        <span style="font-size:0.7em;color:#3a4a65;">{len(category_scores)} categories</span>
                    </div>
                    {bars_html}
                </div>
                """, unsafe_allow_html=True)

            with why_col:
                pos_html = ""
                for drv in result.get("drivers_pos_detailed", [])[:2]:
                    impact_str = drv.get('impact', '+5%')
                    # Extract numeric delta if possible
                    import re as _re
                    _m = _re.search(r'(\d+)', str(impact_str))
                    delta_num = _m.group(1) if _m else "5"
                    desc = drv['explanation'][:72] + "…" if len(drv['explanation']) > 72 else drv['explanation']
                    pos_html += f"""
                    <div class="signal sig-pos">
                        <div class="sig-icon si-up">↑</div>
                        <div class="sig-body"><div class="sig-title">{drv['title']}</div><div class="sig-desc">{desc}</div></div>
                        <span class="sig-delta sd-pos">+{delta_num}%</span>
                    </div>"""

                neg_html = ""
                for drv in result.get("drivers_neg_detailed", [])[:2]:
                    impact_str = drv.get('impact', '-5%')
                    _m2 = _re.search(r'(\d+)', str(impact_str))
                    delta_num2 = _m2.group(1) if _m2 else "4"
                    desc2 = drv['explanation'][:72] + "…" if len(drv['explanation']) > 72 else drv['explanation']
                    neg_html += f"""
                    <div class="signal sig-neg">
                        <div class="sig-icon si-dn">↓</div>
                        <div class="sig-body"><div class="sig-title">{drv['title']}</div><div class="sig-desc">{desc2}</div></div>
                        <span class="sig-delta sd-neg">-{delta_num2}%</span>
                    </div>"""

                st.markdown(f"""
                <div class="vc-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                        <span class="vc-card-title" style="margin-bottom:0;">Why This Score</span>
                    </div>
                    <div style="font-size:0.65em;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#10b981;margin-bottom:6px;">Positive Signals</div>
                    {pos_html}
                    <div style="font-size:0.65em;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#ef4444;margin:10px 0 6px;">Risk Factors</div>
                    {neg_html}
                </div>
                """, unsafe_allow_html=True)

            # ── NEW: STAGE BENCHMARKS ───────────────────────────────────
            _stage = deal.get('stage', 'Seed')
            _bench = {
                "Pre-Seed": {"ARR": "$100K", "Growth": "15%", "Runway": "18 mo"},
                "Seed":     {"ARR": "$500K", "Growth": "20%", "Runway": "18 mo"},
                "Series A": {"ARR": "$2M",   "Growth": "30%", "Runway": "24 mo"},
                "Series B+":{"ARR": "$10M",  "Growth": "50%", "Runway": "24 mo"},
            }.get(_stage, {"ARR": "$500K", "Growth": "20%", "Runway": "18 mo"})

            _arr_vs = "above" if arr_val >= 500_000 else "below"
            _arr_color = "#34d399" if _arr_vs == "above" else "#f87171"
            _growth_color = "#34d399" if growth_pct >= 20 else "#f87171" if growth_pct < 10 else "#fbbf24"
            _run_color = "#34d399" if runway >= 18 else "#f87171" if runway < 12 else "#fbbf24"

            st.markdown(f"""
            <div class="vc-card">
                <div class="vc-card-title">Stage Benchmarks vs. {_stage} Median</div>
                <div class="bench-row">
                    <span class="bl">ARR</span>
                    <span class="bv" style="color:{_arr_color};">{arr_display}</span>
                    <span class="ba">median {_bench['ARR']}</span>
                </div>
                <div class="bench-row">
                    <span class="bl">Growth MoM</span>
                    <span class="bv" style="color:{_growth_color};">{growth_pct:.0f}%</span>
                    <span class="ba">median {_bench['Growth']}</span>
                </div>
                <div class="bench-row">
                    <span class="bl">Runway</span>
                    <span class="bv" style="color:{_run_color};">{runway} mo</span>
                    <span class="ba">median {_bench['Runway']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── NEW: DEAL MOMENTUM / URGENCY ────────────────────────────
            if runway <= 12:
                urg_bg = "rgba(239,68,68,0.07)"; urg_bd = "rgba(239,68,68,0.18)"; urg_tc = "#f87171"
                urg_msg = f"⚡  High urgency — only {runway} months runway remaining. Decision window is closing."
            elif runway <= 18:
                urg_bg = "rgba(245,158,11,0.07)"; urg_bd = "rgba(245,158,11,0.18)"; urg_tc = "#fbbf24"
                urg_msg = f"⏳  Moderate urgency — {runway} months runway. Aim to decide within 30 days."
            else:
                urg_bg = "rgba(16,185,129,0.07)"; urg_bd = "rgba(16,185,129,0.18)"; urg_tc = "#34d399"
                urg_msg = f"✓  Comfortable runway — {runway} months. No immediate pressure; thorough diligence recommended."

            st.markdown(f"""
            <div style="background:{urg_bg};border:1px solid {urg_bd};border-radius:10px;padding:11px 15px;margin-bottom:1rem;font-size:0.84em;font-weight:500;color:{urg_tc};">
                {urg_msg}
            </div>
            """, unsafe_allow_html=True)

            # ── KEY METRICS CHECKLIST ───────────────────────────────────
            with st.expander("📋 Key Metrics Checklist", expanded=False):
                avail_n = sum(1 for v in missing_metrics.values() if v)
                st.caption(f"{avail_n} of {len(missing_metrics)} metrics available")
                cc1, cc2 = st.columns(2)
                for i, (metric, available) in enumerate(missing_metrics.items()):
                    with [cc1, cc2][i % 2]:
                        icon = "✅" if available else "⚠️"
                        col_m = "#34d399" if available else "#f59e0b"
                        st.markdown(f"<span style='color:{col_m};font-size:0.88em;'>{icon} {metric}</span>", unsafe_allow_html=True)

            # ── FULL DRIVER DETAILS ──────────────────────────────────────
            with st.expander("📈 All Positive Drivers", expanded=False):
                for drv in result.get("drivers_pos_detailed", []):
                    st.markdown(f"**✓ {drv['title']}**")
                    st.markdown(drv['explanation'])
                    st.markdown(f"*Impact: {drv['impact']}*")
                    st.markdown("---")

            with st.expander("⚠️ All Risk Factors", expanded=False):
                for drv in result.get("drivers_neg_detailed", []):
                    st.markdown(f"**⚠ {drv['title']}**")
                    st.markdown(drv['explanation'])
                    st.markdown(f"*Impact: {drv['impact']}*")
                    st.markdown("---")

            with st.expander("🚩 Red Flags & Missing Info", expanded=False):
                for flag in result.get("risk_flags_detailed", []):
                    st.markdown(f"**🚩 {flag['title']}**")
                    st.markdown(flag['explanation'])
                    if flag.get('risk_level'):
                        st.markdown(f"*Risk Level: {flag['risk_level']}*")
                    st.markdown("---")

            st.markdown('<div style="border-top:1px solid #1e2a40;margin:1.5rem 0;"></div>', unsafe_allow_html=True)

            # ── GENERATE CONTENT ─────────────────────────────────────────
            st.markdown('<div class="sec-lbl">Generate Content</div>', unsafe_allow_html=True)
            gc1, gc2, gc3 = st.columns(3)

            with gc1:
                if st.button("❓ Diligence Questions", use_container_width=True):
                    client = get_openai_client()
                    if client:
                        with st.spinner("Generating..."):
                            st.session_state.founder_questions = generate_founder_questions(deal, client)
                        st.rerun()

            with gc2:
                if st.button("✉️ Follow-up Email", use_container_width=True):
                    client = get_openai_client()
                    if client:
                        with st.spinner("Drafting..."):
                            st.session_state.founder_followup = generate_founder_followup(deal, result, missing_metrics, client)
                        st.rerun()

            with gc3:
                if st.button("📝 IC Memo", use_container_width=True):
                    client = get_openai_client()
                    if client:
                        with st.spinner("Drafting memo..."):
                            st.session_state.ic_memo = generate_ic_memo(deal, result, client)
                        st.rerun()

            # Display generated content
            if st.session_state.founder_questions:
                st.markdown('<div style="border-top:1px solid #1e2a40;margin:1.25rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**❓ Diligence Questions**")
                st.write(st.session_state.founder_questions)

            if st.session_state.founder_followup:
                st.markdown('<div style="border-top:1px solid #1e2a40;margin:1.25rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**✉️ Follow-up Email**")
                st.code(st.session_state.founder_followup, language=None)
                if st.session_state.founder_email:
                    import urllib.parse
                    mailto_link = f"mailto:{st.session_state.founder_email}?subject={urllib.parse.quote('Follow-up: ' + deal.get('company',''))}&body={urllib.parse.quote(st.session_state.founder_followup)}"
                    st.markdown(f'<a href="{mailto_link}" target="_blank"><button style="padding:8px 16px;background:#2563eb;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:600;font-size:0.87em;">📧 Open in Email Client</button></a>', unsafe_allow_html=True)
                else:
                    st.caption("No contact email found in deck — add it to Notes for mailto link")

            if st.session_state.ic_memo:
                st.markdown('<div style="border-top:1px solid #1e2a40;margin:1.25rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**📝 Investment Committee Memo**")
                st.write(st.session_state.ic_memo)

        # ── RIGHT PANEL ───────────────────────────────────────────────────
        with right_col:

            # Deal Info card
            growth_vc = "#10b981" if growth_pct > 10 else "#ef4444" if growth_pct <= 0 else "#f59e0b"
            runway_vc = "#10b981" if runway >= 18 else "#f59e0b" if runway >= 12 else "#ef4444"

            st.markdown(f"""
            <div class="vc-card">
                <div class="vc-card-title">Deal Info</div>
                <div class="di-row"><span class="di-lbl">Company</span><span class="di-val" style="color:#60a5fa;font-weight:700;">{deal.get('company','—')}</span></div>
                <div class="di-row"><span class="di-lbl">Stage</span><span class="di-val" style="color:#60a5fa;">{deal.get('stage','—')}</span></div>
                <div class="di-row"><span class="di-lbl">ARR</span><span class="di-val" style="color:#34d399;">{arr_display}</span></div>
                <div class="di-row"><span class="di-lbl">Raising</span><span class="di-val">{raise_display}</span></div>
                <div class="di-row"><span class="di-lbl">Growth MoM</span><span class="di-val" style="color:{growth_vc};">{growth_pct:.0f}%</span></div>
                <div class="di-row"><span class="di-lbl">Runway</span><span class="di-val" style="color:{runway_vc};">{runway} months</span></div>
                <div class="di-row"><span class="di-lbl">Sector</span><span class="di-val" style="font-size:0.8em;">{deal.get('sector','—')}</span></div>
                <div class="di-row"><span class="di-lbl">Updated</span><span class="di-val" style="color:#3a4a65;">{datetime.now().strftime('%b %d · %H:%M')}</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Save Deal
            st.markdown('<div class="sec-lbl" style="margin-top:0.25rem;">Save Deal</div>', unsafe_allow_html=True)

            suggested_list = "active" if decision == "Proceed" else "watchlist" if decision == "Watch" else "passed"
            existing_deal = next((d for d in st.session_state.saved_deals if d.get("company") == deal.get("company")), None)
            current_status = existing_deal["status"] if existing_deal else suggested_list
            if current_status not in ["watchlist", "active", "reviewed", "passed"]:
                current_status = {"inbound": "watchlist", "reviewing": "active", "diligencing": "active"}.get(current_status, "watchlist")

            save_status = st.selectbox(
                "Pipeline list",
                options=["watchlist", "active", "reviewed", "passed"],
                index=["watchlist", "active", "reviewed", "passed"].index(current_status),
                format_func=lambda x: {"watchlist": "📌 Watchlist", "active": "⚡ Active", "reviewed": "📋 Reviewed", "passed": "❌ Passed"}[x],
                key="save_status_select",
                label_visibility="collapsed"
            )
            save_tags = st.text_input(
                "Tags",
                value=", ".join(existing_deal.get("tags", [])) if existing_deal else "",
                placeholder="e.g., b2b, high-growth, warm-intro",
                key="save_tags_input",
                label_visibility="collapsed"
            )
            if st.button("💾 Save Deal", use_container_width=True, type="primary", key="save_deal_btn"):
                saved_status = save_deal_to_list(deal, result, save_status, save_tags)
                st.toast(f"✅ Saved to {saved_status.capitalize()}!")
                st.rerun()
            if existing_deal:
                st.caption(f"Last saved: {existing_deal.get('updated_at', '')[:10]}")

            # Quick Copilot
            st.markdown('<div class="sec-lbl" style="margin-top:1.25rem;">Quick Copilot</div>', unsafe_allow_html=True)

            for _emoji, _label in [("🎯", "Competitive analysis"), ("💰", "Unit economics deep dive"), ("📊", "Market sizing"), ("🚨", "Risk assessment")]:
                if st.button(f"{_emoji}  {_label}", key=f"qc_{_label}", use_container_width=True):
                    st.session_state.active_tab = "Copilot"
                    st.rerun()

            st.markdown('<div style="margin-top:0.5rem;"></div>', unsafe_allow_html=True)
            quick_ask = st.text_input("", placeholder="Ask about this deal…", key="quick_ask", label_visibility="collapsed")
            if quick_ask:
                st.session_state.active_tab = "Copilot"
                st.rerun()

elif st.session_state.active_tab == "Copilot":
    st.markdown('<div class="form-section-title">🤖 VCaaS Copilot</div>', unsafe_allow_html=True)
    st.markdown("Ask questions about the current deal. Copilot understands your deal details and investor profile.")
    
    if not st.session_state.last_deal:
        st.info("👈 Complete deal intake and run analysis to activate Copilot.")
    else:
        deal = st.session_state.last_deal
        
        # Quick actions
        st.markdown('<div class="form-section-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Competitive analysis", use_container_width=True):
                st.info("What are the top 3 competitors and how does this company differentiate?")
        
        with col2:
            if st.button("💰 Unit economics deep dive", use_container_width=True):
                st.info("What questions should we ask about CAC, LTV, and payback period?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Market sizing", use_container_width=True):
                st.info("Is the TAM large enough and is this company positioned to capture it?")
        
        with col2:
            if st.button("🚨 Risk assessment", use_container_width=True):
                st.info("What are the key execution and market risks for this stage?")
        
        st.divider()
        
        # Chat
        st.markdown('<div class="form-section-title">💬 Chat</div>', unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        user_input = st.chat_input("Ask me anything about this deal...", key="copilot_input")
        
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.write(user_input)
            
            client = get_openai_client()
            if client:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        system = f"""You are an expert VC analyst. Answer questions about this deal:
Company: {deal.get('company')}
Stage: {deal.get('stage')}
Sector: {deal.get('sector')}
Raise: ${deal.get('raise_amount_usd', 0):,}
ARR: ${deal.get('arr_usd', 0):,}
Growth: {deal.get('growth_rate_pct', 0)}%
Runway: {deal.get('runway_months', 0)} months

Be concise, data-driven, and act like an operating partner."""
                        
                        try:
                            resp = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": system},
                                    {"role": "user", "content": user_input}
                                ],
                                temperature=0.7,
                            )
                            answer = resp.choices[0].message.content.strip()
                            st.write(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
