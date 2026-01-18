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
    initial_sidebar_state="collapsed"
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
if "investor_prefs" not in st.session_state:
    st.session_state.investor_prefs = None

if "extracted_highlights" not in st.session_state:
    st.session_state.extracted_highlights = None

if "founder_questions" not in st.session_state:
    st.session_state.founder_questions = None

if "ic_memo" not in st.session_state:
    st.session_state.ic_memo = None

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

# ========================================
# HELPER FUNCTIONS
# ========================================

def get_openai_client():
    """Get OpenAI client safely."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("🔑 OpenAI API Key", type="password", key="api_key_input")
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
    
    return {
        "prob_next_round": prob,
        "confidence": 0.72,
        "drivers_pos": [
            "Strong growth trajectory",
            "Clear market opportunity",
            "Experienced team",
        ],
        "drivers_neg": [
            "Competitive market",
            "Limited runway",
            "Team background needs verification",
        ],
        "risk_flags": ["Retention metrics not provided", "CAC not provided"] if arr > 0 else ["No revenue metric"],
        "reasoning": reasoning,
    }

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
# MAIN TAB INTERFACE
# ========================================
tab_intake, tab_analysis, tab_copilot = st.tabs(["📥 Intake", "📊 Analysis", "💬 Copilot"])

# ==================================================
# TAB 1: INTAKE
# ==================================================
with tab_intake:
    st.markdown('<div class="form-section-title">📄 Documents & Data</div>', unsafe_allow_html=True)
    
    # Document upload
    with st.form("doc_upload_form"):
        st.markdown("**Upload your deal documents** (pitch deck, financials, etc.)", help="Supported: PDF, PPTX, CSV, Excel, TXT")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            deck = st.file_uploader("Pitch Deck (PDF/PPTX)", type=["pdf", "pptx"], label_visibility="collapsed", key="deck")
        with col2:
            extra = st.file_uploader("Additional Documents", type=["pdf", "pptx", "txt"], accept_multiple_files=True, label_visibility="collapsed", key="extra")
        with col3:
            financials = st.file_uploader("Financials (CSV/Excel)", type=["csv", "xlsx"], label_visibility="collapsed", key="fin")
        
        col_extract, col_preview = st.columns(2)
        with col_extract:
            extract_btn = st.form_submit_button("🔍 Extract Fields from Docs", use_container_width=True)
        
        with col_preview:
            if st.session_state.docs_text:
                preview_len = len(st.session_state.docs_text)
                st.metric("Documents Loaded", f"{preview_len:,} chars", label_visibility="collapsed")
        
        if extract_btn:
            # Process documents
            docs_parts = []
            
            if deck:
                if deck.name.endswith(".pdf"):
                    docs_parts.append(pdf_to_text(deck))
                elif deck.name.endswith(".pptx"):
                    docs_parts.append(pptx_to_text(deck))
            
            if extra:
                for f in extra:
                    if f.name.endswith(".pdf"):
                        docs_parts.append(pdf_to_text(f))
                    elif f.name.endswith(".pptx"):
                        docs_parts.append(pptx_to_text(f))
                    elif f.name.endswith(".txt"):
                        docs_parts.append(txt_to_text(f))
            
            if financials:
                docs_parts.append(tabular_to_text(financials))
            
            st.session_state.docs_text = "\n".join(docs_parts)
            
            if st.session_state.docs_text:
                client = get_openai_client()
                if client:
                    with st.spinner("🤖 Extracting deal fields..."):
                        st.session_state.extracted = extract_fields_from_doc(st.session_state.docs_text, client)
                    
                    if st.session_state.extracted:
                        st.success("✅ Extraction successful!")
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
            value=st.session_state.get("company") or "",
            key="company_intake",
            placeholder="e.g., TechCorp AI"
        )
        st.session_state.company = company_input
        
        sector_input = st.text_input(
            "Sector",
            value=st.session_state.get("sector") or "",
            key="sector_intake",
            placeholder="e.g., B2B SaaS, AI, Climate Tech"
        )
        st.session_state.sector = sector_input
    
    with col2:
        st.markdown("**Funding**")
        stage_select = st.selectbox(
            "Stage",
            ["Pre-Seed", "Seed", "Series A", "Series B+"],
            index=(["Pre-Seed", "Seed", "Series A", "Series B+"].index(st.session_state.get("stage")) if st.session_state.get("stage") in ["Pre-Seed", "Seed", "Series A", "Series B+"] else 0),
            key="stage_intake"
        )
        st.session_state.stage = stage_select
        
        raise_input = st.number_input(
            "Raise amount ($)",
            min_value=0,
            step=250000,
            value=st.session_state.get("raise_amount_usd") or 0,
            key="raise_intake",
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
            value=st.session_state.get("arr_usd") or 0,
            key="arr_intake",
            format="%d"
        )
        st.session_state.arr_usd = arr_input if arr_input > 0 else None
        
        growth_input = st.number_input(
            "Growth rate (%)",
            min_value=0,
            max_value=500,
            step=1,
            value=st.session_state.get("growth_rate_pct") or 0,
            key="growth_intake"
        )
        st.session_state.growth_rate_pct = growth_input if growth_input > 0 else None
    
    with col2:
        st.markdown("**Health**")
        runway_input = st.number_input(
            "Runway (months)",
            min_value=0,
            max_value=60,
            step=1,
            value=st.session_state.get("runway_months") or 0,
            key="runway_intake"
        )
        st.session_state.runway_months = runway_input if runway_input > 0 else None
    
    st.markdown("**Additional Context**")
    notes_input = st.text_area(
        "Notes",
        value=st.session_state.get("notes") or "",
        height=100,
        placeholder="Founder email, diligence notes, meeting summary, red flags, etc.",
        key="notes_intake"
    )
    st.session_state.notes = notes_input if notes_input.strip() else None
    
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
                st.session_state.ic_memo = None
                
                st.success("✅ Analysis complete! Switch to Analysis tab.")
            else:
                st.error("❌ Please fix validation issues above.")

# ==================================================
# TAB 2: ANALYSIS
# ==================================================
with tab_analysis:
    if not st.session_state.last_result:
        st.info("👈 Complete deal intake and run analysis to see results.")
    else:
        deal = st.session_state.last_deal
        result = st.session_state.last_result
        thesis = compute_thesis_fit(deal, st.session_state.investor_prefs)
        rec = generate_recommendation(result["prob_next_round"], thesis)
        
        # Recommendation
        st.markdown('<div class="form-section-title">💼 Investment Recommendation</div>', unsafe_allow_html=True)
        
        col_rec, col_conf = st.columns(2)
        with col_rec:
            badge_class = f"recommendation-badge-{rec['recommendation'].lower()}"
            st.markdown(f'<div class="{badge_class}">{rec["recommendation"]}</div>', unsafe_allow_html=True)
        
        with col_conf:
            conf_color = {"High": "#34c759", "Medium": "#ff9500", "Low": "#ff3b30"}[rec["confidence"]]
            st.metric("Confidence", rec["confidence"], label_visibility="collapsed")
        
        st.divider()
        
        # Key metrics
        st.markdown('<div class="form-section-title">📈 Key Metrics</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Probability", f"{result['prob_next_round']:.0%}")
        with col2:
            st.metric("Stage", deal["stage"])
        with col3:
            st.metric("ARR", f"${deal['arr_usd']:,}")
        with col4:
            st.metric("Growth", f"{deal['growth_rate_pct']}%")
        
        if thesis:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Thesis Fit", f"{thesis['score']}/100")
        
        st.divider()
        
        # Drivers
        st.markdown('<div class="form-section-title">✅ Positive Drivers</div>', unsafe_allow_html=True)
        for driver in result["drivers_pos"]:
            st.markdown(f'<div class="driver-positive">• {driver}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section-title">⚠️ Risk Drivers</div>', unsafe_allow_html=True)
        for driver in result["drivers_neg"]:
            st.markdown(f'<div class="driver-negative">• {driver}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section-title">🚩 Missing Info</div>', unsafe_allow_html=True)
        for flag in result["risk_flags"]:
            st.markdown(f'<div class="driver-flag">• {flag}</div>', unsafe_allow_html=True)
        
        # Reasoning
        with st.expander("📋 Model Reasoning", expanded=True):
            for i, reason in enumerate(result["reasoning"], 1):
                st.write(f"**{i}.** {reason}")
        
        st.divider()
        
        # Generate outputs
        st.markdown('<div class="form-section-title">🚀 Generate Content</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("❓ Founder Diligence Questions", use_container_width=True):
                client = get_openai_client()
                if client:
                    with st.spinner("Generating questions..."):
                        st.session_state.founder_questions = generate_founder_questions(deal, client)
                    st.rerun()
        
        with col2:
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
        
        if st.session_state.ic_memo:
            st.divider()
            st.markdown("### 📝 Investment Committee Memo")
            st.write(st.session_state.ic_memo)
            if st.button("📋 Copy Memo", key="copy_memo"):
                st.toast("Copied to clipboard!")

# ==================================================
# TAB 3: COPILOT
# ==================================================
with tab_copilot:
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
