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
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    :root {
        --primary: #0071e3;
        --success: #34c759;
        --warning: #ff9500;
        --danger: #ff3b30;
        --dark: #000000;
        --light: #f5f5f7;
        --gray: #86868b;
        --border: #e5e5ea;
    }
    
    /* Main title */
    .main-title {
        font-size: 2.5em;
        font-weight: 700;
        color: #000000;
        letter-spacing: -0.03em;
        margin-bottom: 0.25rem;
    }
    
    .subtitle {
        font-size: 1em;
        color: #86868b;
        font-weight: 400;
    }
    
    /* Deal header */
    .deal-header {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 18px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    .deal-header-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 2rem;
        margin-bottom: 1rem;
    }
    
    .deal-header-item {
        border-right: 1px solid #e5e5ea;
        padding-right: 2rem;
    }
    
    .deal-header-item:last-child {
        border-right: none;
        padding-right: 0;
    }
    
    .deal-header-label {
        font-size: 0.8125em;
        color: #86868b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.015em;
        margin-bottom: 0.5rem;
    }
    
    .deal-header-value {
        font-size: 1.3125em;
        font-weight: 600;
        color: #000000;
        letter-spacing: -0.01em;
    }
    
    /* Progress indicator */
    .progress-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .progress-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.9375em;
        color: #000000;
    }
    
    .progress-check {
        font-size: 1.25em;
        color: #34c759;
    }
    
    .progress-pending {
        font-size: 1.25em;
        color: #e5e5ea;
    }
    
    /* Form section */
    .form-section {
        background: #ffffff;
        border-radius: 18px;
        padding: 2rem;
        border: 1px solid #e5e5ea;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 2rem;
    }
    
    .form-section-title {
        font-size: 1.125em;
        font-weight: 600;
        color: #000000;
        margin-bottom: 1.5rem;
        letter-spacing: -0.01em;
    }
    
    .form-label {
        font-size: 0.9375em;
        font-weight: 500;
        color: #000000;
        margin-bottom: 0.5rem;
    }
    
    .form-hint {
        font-size: 0.8125em;
        color: #86868b;
        margin-bottom: 1.25rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        font-size: 1em !important;
        padding: 0.75rem !important;
        border-radius: 8px !important;
        border: 1px solid #e5e5ea !important;
        background-color: #ffffff !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0071e3 !important;
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.95em !important;
        padding: 0.75rem 1.5rem !important;
        letter-spacing: -0.01em;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #0071e3 !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #0066cc !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #f5f5f7 !important;
        color: #0071e3 !important;
        border: 1px solid #e5e5ea !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #e5e5ea !important;
    }
    
    /* Cards */
    .metric-card {
        background: #f5f5f7;
        border-radius: 12px;
        padding: 1.25rem;
        border: none;
    }
    
    .recommendation-card {
        background: #ffffff;
        border: 2px solid #0071e3;
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    .recommendation-badge-invest {
        display: inline-block;
        background: #34c759;
        color: white;
        padding: 0.875rem 1.75rem;
        border-radius: 12px;
        font-size: 1.3125em;
        font-weight: 600;
        margin: 0.5rem;
    }
    
    .recommendation-badge-watchlist {
        display: inline-block;
        background: #ff9500;
        color: white;
        padding: 0.875rem 1.75rem;
        border-radius: 12px;
        font-size: 1.3125em;
        font-weight: 600;
        margin: 0.5rem;
    }
    
    .recommendation-badge-pass {
        display: inline-block;
        background: #ff3b30;
        color: white;
        padding: 0.875rem 1.75rem;
        border-radius: 12px;
        font-size: 1.3125em;
        font-weight: 600;
        margin: 0.5rem;
    }
    
    /* Driver cards */
    .driver-positive {
        background: #d1f4e0;
        border-left: 3px solid #34c759;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .driver-negative {
        background: #fff8e1;
        border-left: 3px solid #ff9500;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .driver-flag {
        background: #ffe0e0;
        border-left: 3px solid #ff3b30;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Extraction preview */
    .extraction-preview {
        background: #f5f5f7;
        border: 1px solid #e5e5ea;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.85em;
        max-height: 300px;
        overflow-y: auto;
    }
    
    /* Expander */
    .streamlit-expander {
        border: 1px solid #e5e5ea !important;
        border-radius: 12px !important;
        background: #ffffff !important;
    }
    
    /* Divider */
    .stDivider {
        margin: 2rem 0 !important;
    }
    
    /* Status badge */
    .status-ready {
        display: inline-block;
        background: #d1f4e0;
        color: #057857;
        padding: 0.375rem 0.875rem;
        border-radius: 8px;
        font-size: 0.75em;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .status-pending {
        display: inline-block;
        background: #fff8e1;
        color: #b57200;
        padding: 0.375rem 0.875rem;
        border-radius: 8px;
        font-size: 0.75em;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Toast/info */
    .info-box {
        background: #dbeafe;
        border: 1px solid #0071e3;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        color: #0066cc;
        font-size: 0.95em;
    }
    
    .warning-box {
        background: #fff8e1;
        border: 1px solid #ff9500;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        color: #b57200;
        font-size: 0.95em;
    }
    
    /* Column layout fix */
    .stColumn > div > div {
        width: 100%;
    }
    
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
col_title, col_reset = st.columns([1, 0.2])
with col_title:
    st.markdown('<div class="main-title">VCaaS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Deal Intake & Analysis Platform</div>', unsafe_allow_html=True)

with col_reset:
    if st.button("🔄 Reset Deal", use_container_width=True, help="Clear all fields"):
        reset_deal()
        st.rerun()

# ========================================
# SIDEBAR: AUTHENTICATION & INVESTOR PROFILE
# ========================================
with st.sidebar:
    # Authentication section
    if not st.session_state.logged_in:
        st.markdown("### 🔐 Login / Signup")
        
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
        st.markdown(f"### 👤 {st.session_state.current_user}")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        st.divider()
    
    # Investor Profile section (only shown when logged in)
    if st.session_state.logged_in:
        st.markdown("### ⚙️ Investor Profile")
    
    col_pref, col_toggle = st.columns([1, 0.3])
    with col_pref:
        st.markdown("**Your preferences**")
    with col_toggle:
        if st.button("✏️", help="Edit preferences", key="edit_prefs"):
            st.session_state.show_prefs_onboard = not st.session_state.show_prefs_onboard
            st.rerun()
    
    if st.session_state.investor_prefs:
        st.markdown(f"**Name:** {st.session_state.investor_prefs.get('investor_name', '—')}")
        st.markdown(f"**Stage:** {st.session_state.investor_prefs.get('preferred_stage', 'Any')}")
        st.markdown(f"**Sector:** {st.session_state.investor_prefs.get('preferred_sector', 'Any')}")
        st.markdown(f"**Min ARR:** ${st.session_state.investor_prefs.get('min_arr', 0):,}")
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
        st.markdown("### 📁 Deal Pipeline")
        
        # Pipeline metrics
        watchlist_count = len([d for d in st.session_state.saved_deals if d.get("status") == "watchlist"])
        active_count = len([d for d in st.session_state.saved_deals if d.get("status") == "active"])
        reviewed_count = len([d for d in st.session_state.saved_deals if d.get("status") == "reviewed"])
        passed_count = len([d for d in st.session_state.saved_deals if d.get("status") == "passed"])
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📌", watchlist_count, help="Watchlist")
        col2.metric("⚡", active_count, help="Active")
        col3.metric("📋", reviewed_count, help="Reviewed")
        col4.metric("❌", passed_count, help="Passed")
        
        st.divider()
        
        # List selector tabs
        list_tabs = st.segmented_control(
            "Select List",
            options=["watchlist", "active", "reviewed", "passed"],
            format_func=lambda x: {"watchlist": "Watchlist", "active": "Active", "reviewed": "Reviewed", "passed": "Passed"}[x],
            default=st.session_state.active_list,
            label_visibility="collapsed"
        )
        
        if list_tabs:
            st.session_state.active_list = list_tabs
        
        # Filters section
        with st.expander("🔍 Filters", expanded=False):
            # Stage filter
            all_stages = ["Pre-Seed", "Seed", "Series A", "Series B+"]
            stage_filter = st.multiselect(
                "Stage",
                options=all_stages,
                default=st.session_state.deal_filters["stages"]
            )
            st.session_state.deal_filters["stages"] = stage_filter
            
            # Sector filter
            all_sectors = list(set([d.get("sector") for d in st.session_state.saved_deals if d.get("sector")]))
            sector_filter = st.multiselect(
                "Sector",
                options=sorted(all_sectors),
                default=[s for s in st.session_state.deal_filters["sectors"] if s in all_sectors]
            )
            st.session_state.deal_filters["sectors"] = sector_filter
            
            # Decision filter
            decision_filter = st.multiselect(
                "Decision",
                options=["Proceed", "Watch", "Pass"],
                default=st.session_state.deal_filters["decisions"]
            )
            st.session_state.deal_filters["decisions"] = decision_filter
            
            # Min ARR
            min_arr_filter = st.number_input(
                "Min ARR ($)",
                min_value=0,
                step=100000,
                value=st.session_state.deal_filters["min_arr"]
            )
            st.session_state.deal_filters["min_arr"] = min_arr_filter
            
            # Search
            search_filter = st.text_input(
                "Search company",
                value=st.session_state.deal_filters["search"],
                placeholder="Company name..."
            )
            st.session_state.deal_filters["search"] = search_filter
            
            # Sort
            sort_filter = st.selectbox(
                "Sort by",
                options=["last_updated", "probability", "arr"],
                format_func=lambda x: {"last_updated": "Last Updated", "probability": "Probability ↓", "arr": "ARR ↓"}[x],
                index=["last_updated", "probability", "arr"].index(st.session_state.deal_filters["sort_by"])
            )
            st.session_state.deal_filters["sort_by"] = sort_filter
            
            if st.button("🔄 Reset Filters", use_container_width=True):
                st.session_state.deal_filters = {
                    "stages": [],
                    "sectors": [],
                    "decisions": [],
                    "min_arr": 0,
                    "search": "",
                    "sort_by": "last_updated"
                }
                st.rerun()
        
        st.divider()
        
        # Get filtered deals for current list
        filtered_deals = get_filtered_deals(st.session_state.active_list)
        
        st.caption(f"**{len(filtered_deals)} deals** in {st.session_state.active_list.capitalize()}")
        
        # Display deals
        if filtered_deals:
            for deal in filtered_deals[:20]:  # Show max 20 in sidebar
                decision_color = {
                    "Proceed": "#34c759",
                    "Watch": "#ff9500",
                    "Pass": "#ff3b30"
                }.get(deal.get("decision"), "#86868b")
                
                decision_emoji = {
                    "Proceed": "✅",
                    "Watch": "👀",
                    "Pass": "❌"
                }.get(deal.get("decision"), "📄")
                
                with st.container():
                    # Company name button (clickable to load)
                    if st.button(
                        f"{decision_emoji} {deal['company']}",
                        key=f"load_{deal['id']}",
                        use_container_width=True
                    ):
                        load_deal(deal)
                        st.session_state.active_tab = "Analysis"
                        st.toast(f"✅ Loaded {deal['company']}")
                        st.rerun()
                    
                    # Compact info
                    col1, col2, col3 = st.columns(3)
                    col1.caption(deal.get("stage", "—"))
                    col2.caption(f"{deal.get('prob_next_round', 0):.0%}")
                    
                    # Move to list dropdown
                    with col3:
                        new_status = st.selectbox(
                            "Move",
                            options=["watchlist", "active", "reviewed", "passed"],
                            index=["watchlist", "active", "reviewed", "passed"].index(deal.get("status", "watchlist")),
                            format_func=lambda x: {"watchlist": "📌", "active": "⚡", "reviewed": "📋", "passed": "❌"}[x],
                            key=f"status_{deal['id']}",
                            label_visibility="collapsed"
                        )
                        if new_status != deal.get("status"):
                            update_deal_status(deal["id"], new_status)
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info(f"No deals in {st.session_state.active_list.capitalize()}")
    
    elif st.session_state.logged_in:
        st.markdown("### 📁 Deal Pipeline")
        st.info("No saved deals yet. Run analysis and save your first deal!")

# ========================================
# DEAL HEADER (Dynamic)
# ========================================
company = st.session_state.get("company") or "—"
stage = st.session_state.get("stage") or "—"
sector = st.session_state.get("sector") or "—"
timestamp = datetime.now().strftime("%b %d, %H:%M")

st.markdown(f"""
<div class="deal-header">
    <div class="deal-header-row">
        <div class="deal-header-item">
            <div class="deal-header-label">Company</div>
            <div class="deal-header-value">{company}</div>
        </div>
        <div class="deal-header-item">
            <div class="deal-header-label">Stage</div>
            <div class="deal-header-value">{stage}</div>
        </div>
        <div class="deal-header-item">
            <div class="deal-header-label">Sector</div>
            <div class="deal-header-value">{sector}</div>
        </div>
        <div class="deal-header-item">
            <div class="deal-header-label">Last Updated</div>
            <div class="deal-header-value">{timestamp}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========================================
# PROGRESS INDICATOR
# ========================================
docs_up, fields_filled, analysis_done = get_progress_status()

col1, col2, col3, col4 = st.columns(4, gap="small")
with col1:
    check = "✓" if docs_up else "○"
    color = "#34c759" if docs_up else "#e5e5ea"
    st.markdown(f'<span style="color: {color}; font-size: 1.5em; margin-right: 0.5rem;">{check}</span><b>Docs Uploaded</b>', unsafe_allow_html=True)

with col2:
    check = "✓" if st.session_state.extracted else "○"
    color = "#34c759" if st.session_state.extracted else "#e5e5ea"
    st.markdown(f'<span style="color: {color}; font-size: 1.5em; margin-right: 0.5rem;">{check}</span><b>Fields Extracted</b>', unsafe_allow_html=True)

with col3:
    check = "✓" if fields_filled else "○"
    color = "#34c759" if fields_filled else "#e5e5ea"
    st.markdown(f'<span style="color: {color}; font-size: 1.5em; margin-right: 0.5rem;">{check}</span><b>Fields Filled</b>', unsafe_allow_html=True)

with col4:
    check = "✓" if analysis_done else "○"
    color = "#34c759" if analysis_done else "#e5e5ea"
    st.markdown(f'<span style="color: {color}; font-size: 1.5em; margin-right: 0.5rem;">{check}</span><b>Analyzed</b>', unsafe_allow_html=True)

st.divider()

# ========================================
# CUSTOM TAB BUTTONS
# ========================================
col1, col2, col3 = st.columns(3, gap="small")
with col1:
    if st.button("📥 Intake", use_container_width=True, type="primary" if st.session_state.active_tab == "Intake" else "secondary"):
        scroll_to_top()
        st.session_state.active_tab = "Intake"
        st.rerun()

with col2:
    if st.button("📊 Analysis", use_container_width=True, type="primary" if st.session_state.active_tab == "Analysis" else "secondary"):
        scroll_to_top()
        st.session_state.active_tab = "Analysis"
        st.rerun()

with col3:
    if st.button("💬 Copilot", use_container_width=True, type="primary" if st.session_state.active_tab == "Copilot" else "secondary"):
        scroll_to_top()
        st.session_state.active_tab = "Copilot"
        st.rerun()

st.divider()

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
        st.info("👈 Complete deal intake and run analysis to see results.")
    else:
        deal = st.session_state.last_deal
        result = st.session_state.last_result
        prob = result["prob_next_round"]
        confidence = result.get("confidence", 0.72)
        
        # Calculate scores and metrics WITH PERSONALIZATION
        category_scores, personalization_applied = calculate_category_scores(deal, st.session_state.investor_prefs)
        missing_metrics = check_missing_metrics(deal)
        decision, decision_emoji = get_investment_decision(prob)
        
        # Investment Decision Summary Card
        st.markdown('<div class="form-section-title">📊 Investment Decision</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            decision_color = {"Proceed": "#34c759", "Watch": "#ff9500", "Pass": "#ff3b30"}[decision]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {decision_color}15, {decision_color}08); 
                        border-left: 4px solid {decision_color}; 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin-bottom: 10px;">
                <div style="font-size: 14px; color: #86868b; margin-bottom: 8px;">RECOMMENDATION</div>
                <div style="font-size: 32px; font-weight: 600; color: {decision_color}; margin-bottom: 4px;">
                    {decision_emoji} {decision}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Probability", f"{prob:.0%}", help="Likelihood of raising next round")
        
        with col3:
            st.metric("Confidence", f"{int(confidence * 100)}%", help="Model confidence in prediction")
        
        # Show personalization if applied
        if personalization_applied:
            st.markdown("**🎯 Personalization Applied:**")
            for item in personalization_applied:
                st.caption(f"• {item}")
        
        st.divider()
        
        # Color-coded tags for deal attributes
        st.markdown("### 🏷️ Deal Overview")
        
        tag_col1, tag_col2, tag_col3, tag_col4 = st.columns(4)
        
        with tag_col1:
            stage_colors = {
                "Pre-Seed": "#5856d6",
                "Seed": "#007AFF",
                "Series A": "#34c759",
                "Series B+": "#ff9500"
            }
            stage_color = stage_colors.get(deal.get("stage"), "#86868b")
            st.markdown(f"""
            <div style="background: {stage_color}20; border: 1px solid {stage_color}; padding: 8px 12px; border-radius: 20px; text-align: center;">
                <div style="font-size: 11px; color: #86868b; font-weight: 500;">STAGE</div>
                <div style="font-size: 14px; color: {stage_color}; font-weight: 600;">{deal.get('stage', '—')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with tag_col2:
            st.markdown(f"""
            <div style="background: #007AFF20; border: 1px solid #007AFF; padding: 8px 12px; border-radius: 20px; text-align: center;">
                <div style="font-size: 11px; color: #86868b; font-weight: 500;">SECTOR</div>
                <div style="font-size: 14px; color: #007AFF; font-weight: 600;">{deal.get('sector', '—')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with tag_col3:
            arr_val = deal.get('arr_usd', 0)
            arr_display = f"${arr_val/1_000_000:.1f}M" if arr_val >= 1_000_000 else f"${arr_val/1_000:.0f}K" if arr_val >= 1_000 else f"${arr_val}"
            st.markdown(f"""
            <div style="background: #34c75920; border: 1px solid #34c759; padding: 8px 12px; border-radius: 20px; text-align: center;">
                <div style="font-size: 11px; color: #86868b; font-weight: 500;">ARR</div>
                <div style="font-size: 14px; color: #34c759; font-weight: 600;">{arr_display}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with tag_col4:
            raise_val = deal.get('raise_amount_usd', 0)
            raise_display = f"${raise_val/1_000_000:.1f}M" if raise_val >= 1_000_000 else f"${raise_val/1_000:.0f}K" if raise_val >= 1_000 else f"${raise_val}"
            st.markdown(f"""
            <div style="background: #ff950020; border: 1px solid #ff9500; padding: 8px 12px; border-radius: 20px; text-align: center;">
                <div style="font-size: 11px; color: #86868b; font-weight: 500;">RAISING</div>
                <div style="font-size: 14px; color: #ff9500; font-weight: 600;">{raise_display}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Top KPI Row
        st.markdown("### 📊 Key Indicators")
        
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        # Calculate missing info count
        missing_count = sum(1 for available in missing_metrics.values() if not available)
        
        # Calculate time-to-diligence estimate (heuristic)
        base_days = 7
        extra_days = missing_count * 2  # 2 days per missing metric
        time_to_diligence = base_days + extra_days
        
        # Calculate deal quality meter (0-100)
        deal_quality = 50  # Base
        deal_quality += min(20, prob * 30)  # Up to 30 from probability
        deal_quality += min(15, (8 - missing_count) * 2)  # Penalize missing info
        deal_quality += min(15, category_scores.get("Fund Fit", 5) * 1.5)  # Fund fit bonus
        deal_quality = max(0, min(100, deal_quality))
        
        # Calculate investor fit score (0-100)
        fit_score = int(category_scores.get("Fund Fit", 5) * 10)
        
        with kpi_col1:
            st.metric(
                "Next-Round Probability",
                f"{prob:.0%}",
                delta=f"{(prob - 0.62):.0%}" if prob != 0.62 else None,
                help="Likelihood of successfully raising next round"
            )
        
        with kpi_col2:
            st.metric(
                "Investor Fit Score",
                f"{fit_score}/100",
                help="How well this deal matches your preferences"
            )
        
        with kpi_col3:
            st.metric(
                "Missing Info",
                f"{missing_count}/8",
                delta=f"{missing_count} gaps" if missing_count > 0 else "Complete",
                delta_color="inverse",
                help="Critical metrics not provided"
            )
        
        with kpi_col4:
            st.metric(
                "Time to Diligence",
                f"~{time_to_diligence} days",
                help="Estimated time to complete diligence based on missing info"
            )
        
        # Deal Quality Meter
        st.markdown("**Deal Quality Score**")
        quality_color = "#34c759" if deal_quality >= 70 else "#ff9500" if deal_quality >= 50 else "#ff3b30"
        st.progress(deal_quality / 100)
        st.caption(f"Overall quality: {deal_quality:.0f}/100")
        
        st.divider()
        
        # Score Breakdown
        st.markdown('<div class="form-section-title">🎯 Score Breakdown</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        for i, (category, score) in enumerate(category_scores.items()):
            with [col1, col2, col3][i % 3]:
                st.markdown(f"**{category}**")
                st.progress(score / 10.0)
                st.caption(f"{score:.1f}/10")
        
        st.divider()
        
        # Key Missing Metrics
        with st.expander("📋 Key Metrics Checklist", expanded=False):
            missing_count = sum(1 for available in missing_metrics.values() if not available)
            st.caption(f"{len(missing_metrics) - missing_count} of {len(missing_metrics)} metrics available")
            
            col1, col2 = st.columns(2)
            for i, (metric, available) in enumerate(missing_metrics.items()):
                with [col1, col2][i % 2]:
                    status = "✅" if available else "⚠️"
                    color = "#34c759" if available else "#ff9500"
                    st.markdown(f"<span style='color: {color};'>{status} {metric}</span>", unsafe_allow_html=True)
        
        st.divider()
        
        # Why This Score - Top 3 drivers and risks
        st.markdown('<div class="form-section-title">💡 Why This Score?</div>', unsafe_allow_html=True)
        
        col_pos, col_neg = st.columns(2)
        
        with col_pos:
            st.markdown("**Top Drivers**")
            for i, driver_detail in enumerate(result.get("drivers_pos_detailed", [])[:3], 1):
                with st.expander(f"✓ {driver_detail['title']}", expanded=False):
                    st.markdown(driver_detail['explanation'])
                    st.markdown(f"**Impact:** {driver_detail['impact']}")
        
        with col_neg:
            st.markdown("**Top Risks**")
            for i, driver_detail in enumerate(result.get("drivers_neg_detailed", [])[:3], 1):
                with st.expander(f"⚠ {driver_detail['title']}", expanded=False):
                    st.markdown(driver_detail['explanation'])
                    st.markdown(f"**Impact:** {driver_detail['impact']}")
        
        # Full Details in Expanders
        st.divider()
        
        with st.expander("📊 View All Positive Drivers", expanded=False):
            for driver_detail in result.get("drivers_pos_detailed", []):
                st.markdown(f"**✓ {driver_detail['title']}**")
                st.markdown(driver_detail['explanation'])
                st.markdown(f"*Impact: {driver_detail['impact']}*")
                st.markdown("---")
        
        with st.expander("⚠️ View All Risk Drivers", expanded=False):
            for driver_detail in result.get("drivers_neg_detailed", []):
                st.markdown(f"**⚠ {driver_detail['title']}**")
                st.markdown(driver_detail['explanation'])
                st.markdown(f"*Impact: {driver_detail['impact']}*")
                st.markdown("---")
        
        with st.expander("🚩 View All Red Flags & Missing Info", expanded=False):
            for flag_detail in result.get("risk_flags_detailed", []):
                st.markdown(f"**🚩 {flag_detail['title']}**")
                st.markdown(flag_detail['explanation'])
                if flag_detail.get('risk_level'):
                    st.markdown(f"*Risk Level: {flag_detail['risk_level']}*")
                st.markdown("---")
        
        st.divider()
        
        # Save Deal Section - Enhanced with list selection
        st.markdown('<div class="form-section-title">💾 Save This Deal</div>', unsafe_allow_html=True)
        
        # Get suggested list based on decision
        suggested_list = "active" if decision == "Proceed" else "watchlist" if decision == "Watch" else "passed" if decision == "Pass" else "reviewed"
        suggested_label = suggested_list.capitalize()
        
        # Check if deal already exists
        existing_deal = next((d for d in st.session_state.saved_deals if d.get("company") == deal.get("company")), None)
        
        with st.expander("📝 Save Deal Details", expanded=not bool(existing_deal)):
            st.caption(f"💡 Based on '{decision}' recommendation, we suggest saving to: **{suggested_label}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Migrate old status values to new ones
                current_status = existing_deal["status"] if existing_deal else suggested_list
                if current_status not in ["watchlist", "active", "reviewed", "passed"]:
                    # Map old statuses to new ones
                    status_migration = {
                        "inbound": "watchlist",
                        "reviewing": "active",
                        "diligencing": "active"
                    }
                    current_status = status_migration.get(current_status, "watchlist")
                
                save_status = st.selectbox(
                    "Save to List",
                    options=["watchlist", "active", "reviewed", "passed"],
                    index=["watchlist", "active", "reviewed", "passed"].index(current_status),
                    format_func=lambda x: {"watchlist": "📌 Watchlist", "active": "⚡ Active", "reviewed": "📋 Reviewed", "passed": "❌ Passed"}[x],
                    key="save_status_select"
                )
            
            with col2:
                save_tags = st.text_input(
                    "Tags (comma-separated)",
                    value=", ".join(existing_deal.get("tags", [])) if existing_deal else "",
                    placeholder="e.g., fintech, high-growth, founder-led",
                    key="save_tags_input"
                )
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("💾 Save Deal", use_container_width=True, type="primary", key="save_deal_btn"):
                    saved_status = save_deal_to_list(deal, result, save_status, save_tags)
                    status_label = {"watchlist": "Watchlist", "active": "Active", "reviewed": "Reviewed", "passed": "Passed"}[saved_status]
                    st.toast(f"✅ Saved {deal.get('company')} to {status_label}!")
                    st.rerun()
            
            with col_cancel:
                if existing_deal:
                    st.caption(f"Last saved: {existing_deal.get('updated_at', 'Unknown')[:10]}")
        
        st.divider()
        
        # Generate Content Section - Keep existing functionality
        st.markdown('<div class="form-section-title">🚀 Generate Content</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❓ Founder Diligence Questions", use_container_width=True):
                client = get_openai_client()
                if client:
                    with st.spinner("Generating questions..."):
                        st.session_state.founder_questions = generate_founder_questions(deal, client)
                    st.rerun()
        
        with col2:
            if st.button("✉️ Founder Follow-up Email", use_container_width=True):
                client = get_openai_client()
                if client:
                    with st.spinner("Drafting email..."):
                        st.session_state.founder_followup = generate_founder_followup(deal, result, missing_metrics, client)
                    st.rerun()
        
        with col3:
            if st.button("📝 IC Memo", use_container_width=True):
                client = get_openai_client()
                if client:
                    with st.spinner("Drafting memo..."):
                        st.session_state.ic_memo = generate_ic_memo(deal, result, client)
                    st.rerun()
        
        if st.session_state.founder_questions:
            st.divider()
            st.markdown("### ❓ Questions to Ask Founder")
            st.write(st.session_state.founder_questions)
            if st.button("📋 Copy Questions", key="copy_qs"):
                st.toast("Copied to clipboard!")
        
        if st.session_state.founder_followup:
            st.divider()
            st.markdown("### ✉️ Founder Follow-up Email")
            st.code(st.session_state.founder_followup, language=None)
            
            col_copy, col_send, col_empty = st.columns([1, 1, 2])
            with col_copy:
                if st.button("📋 Copy Email", key="copy_followup", use_container_width=True):
                    st.toast("Email copied to clipboard!")
            
            with col_send:
                if st.session_state.founder_email:
                    import urllib.parse
                    
                    # Prepare email components
                    to_email = st.session_state.founder_email
                    subject = f"Follow-up: {deal.get('company', 'Your Company')}"
                    body = st.session_state.founder_followup
                    
                    # Create mailto link
                    mailto_link = f"mailto:{to_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    
                    st.markdown(f'<a href="{mailto_link}" target="_blank"><button style="width: 100%; padding: 0.5rem; background: #007AFF; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">📧 Send Email</button></a>', unsafe_allow_html=True)
                else:
                    if st.button("📧 Send Email", key="send_email_disabled", use_container_width=True, disabled=True):
                        pass
                    st.caption("No contact email found in deck")
        
        if st.session_state.ic_memo:
            st.divider()
            st.markdown("### 📝 Investment Committee Memo")
            st.write(st.session_state.ic_memo)
            if st.button("📋 Copy Memo", key="copy_memo"):
                st.toast("Copied to clipboard!")

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
