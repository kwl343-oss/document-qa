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
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600&display=swap');
    *,*::before,*::after{box-sizing:border-box;}

    :root {
      --bg:#07080c; --s0:#0b0d13; --s1:#0f1117; --s2:#141720;
      --s3:#191d28; --s4:#1e2330; --s5:#232839;
      --b0:rgba(255,255,255,0.04); --b1:rgba(255,255,255,0.07);
      --b2:rgba(255,255,255,0.11); --b3:rgba(255,255,255,0.18);
      --t1:#eeeef2; --t2:#a0a3b8; --t3:#5a5e7a; --t4:#2e3248;
      --blue:#4c8eff; --violet:#7c6af7; --green:#00c27a;
      --amber:#f5a623; --red:#f0455a;
      --font:'Geist',-apple-system,sans-serif;
      --mono:'Geist Mono',monospace;
      --r-sm:6px; --r-md:10px; --r-lg:14px;
    }
    
    /* ===== DARK BASE ===== */
    html,body{background:var(--bg);color:var(--t1);font-family:var(--font);font-size:13px;-webkit-font-smoothing:antialiased;}
    .stApp{background:var(--bg)!important;}
    .main .block-container{padding:0 20px 40px!important;max-width:100%!important;}

    /* === HIDE CHROME === */
    #MainMenu,footer,.stDeployButton,
    [data-testid="stToolbar"],[data-testid="stDecoration"],
    [data-testid="stHeader"],[data-testid="stSidebarNav"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[title="Collapse sidebar"],
    button[title="Open sidebar"]{display:none!important;}

    /* === SIDEBAR === */
    [data-testid="stSidebar"]{background:var(--s0)!important;border-right:1px solid var(--b0)!important;}
    [data-testid="stSidebar"]>div{padding:0!important;}
    [data-testid="stSidebar"] *{font-family:var(--font)!important;}
    section[data-testid="stSidebar"]{width:256px!important;min-width:256px!important;max-width:256px!important;flex-shrink:0!important;}
    [data-testid="stSidebarResizeHandle"]{display:none!important;}
    [data-testid="stSidebarContent"]{width:256px!important;max-width:256px!important;}
    /* Compact all buttons inside sidebar — high specificity to override Streamlit defaults */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] .stButton>button,
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button{
        height:26px!important;min-height:26px!important;max-height:26px!important;
        padding:0 8px!important;font-size:10px!important;font-weight:500!important;
        line-height:1!important;border-radius:6px!important;
        white-space:nowrap!important;overflow:hidden!important;
    }
    /* Compact columns inside sidebar */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]{gap:4px!important;}
    section[data-testid="stSidebar"] [data-testid="column"]{min-width:0!important;overflow:hidden!important;padding:0!important;}
    /* Compact inputs */
    section[data-testid="stSidebar"] .stTextInput>div>div>input{font-size:11px!important;height:28px!important;padding:0 8px!important;}
    section[data-testid="stSidebar"] [data-baseweb="select"]>div{min-height:28px!important;font-size:10px!important;}
    /* Kill default vertical spacing between sidebar elements */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:2px!important;}
    section[data-testid="stSidebar"] div.block-container{padding:0!important;}
    section[data-testid="stSidebar"] .stDivider{margin:3px 0!important;}
    /* Compact captions/text */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stMarkdown p{font-size:11px!important;margin:0!important;color:var(--t2)!important;}
    /* Compact radio row for list filter */
    section[data-testid="stSidebar"] .stRadio{padding:0 8px!important;}
    section[data-testid="stSidebar"] .stRadio label{font-size:10px!important;gap:3px!important;}
    section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"]{display:none!important;}
    /* Deal card margin in sidebar */
    section[data-testid="stSidebar"] .deal-card{margin:0 6px 2px!important;}

    /* === TYPOGRAPHY === */
    h1,h2,h3,h4,h5,h6{font-family:var(--font)!important;color:var(--t1)!important;font-weight:600!important;letter-spacing:-0.02em!important;}
    p,.stMarkdown p,.stMarkdown li{color:var(--t2)!important;font-size:13px!important;line-height:1.5!important;}
    label{color:var(--t3)!important;font-size:10px!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.06em!important;font-family:var(--font)!important;}
    .stCaption p{color:var(--t4)!important;font-size:10px!important;}
    strong{color:var(--t1)!important;}
    /* Tighter element spacing in main area */
    .stMarkdown{line-height:1.4!important;}
    [data-testid="stHorizontalBlock"]{gap:12px!important;}

    /* === INPUTS === */
    .stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea>div>div>textarea{
      background:var(--s2)!important;color:var(--t1)!important;
      border:1px solid var(--b2)!important;border-radius:var(--r-sm)!important;
      font-family:var(--font)!important;font-size:12px!important;
    }
    .stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
      border-color:var(--blue)!important;box-shadow:0 0 0 2px rgba(76,142,255,0.12)!important;
    }
    .stSelectbox>div>div,[data-baseweb="select"]>div{
      background:var(--s2)!important;border:1px solid var(--b2)!important;
      border-radius:var(--r-sm)!important;
    }
    [data-baseweb="select"] *{color:var(--t2)!important;font-family:var(--font)!important;}
    [data-baseweb="menu"]{background:var(--s2)!important;border:1px solid var(--b2)!important;}
    [data-baseweb="option"]:hover{background:var(--s3)!important;}

    /* === BUTTONS === */
    .stButton>button{
      background:transparent!important;color:var(--t3)!important;
      border:1px solid var(--b2)!important;border-radius:var(--r-sm)!important;
      font-family:var(--font)!important;font-size:11px!important;font-weight:500!important;
      height:28px!important;padding:0 10px!important;transition:all 0.1s!important;
    }
    .stButton>button:hover{background:var(--s3)!important;color:var(--t1)!important;border-color:var(--b3)!important;}
    .stButton>button[kind="primary"]{background:var(--blue)!important;border-color:transparent!important;color:white!important;}
    .stButton>button[kind="primary"]:hover{background:#3a7dee!important;}
    .stButton>button[kind="secondary"]{background:var(--s2)!important;color:var(--t2)!important;border-color:var(--b1)!important;}
    .stButton>button[kind="secondary"]:hover{background:var(--s3)!important;color:var(--t1)!important;}
    [data-testid="stFormSubmitButton"]>button{background:var(--blue)!important;color:white!important;border:none!important;}

    /* === EXPANDER === */
    [data-testid="stExpander"]{background:var(--s1)!important;border:1px solid var(--b1)!important;border-radius:var(--r-lg)!important;margin-bottom:8px!important;}
    [data-testid="stExpander"] summary{color:var(--t2)!important;font-size:12px!important;}

    /* === ALERTS === */
    [data-testid="stInfo"]{background:rgba(76,142,255,0.05)!important;border:1px solid rgba(76,142,255,0.15)!important;border-radius:var(--r-md)!important;}
    [data-testid="stWarning"]{background:rgba(245,166,35,0.05)!important;border:1px solid rgba(245,166,35,0.15)!important;border-radius:var(--r-md)!important;}
    [data-testid="stSuccess"]{background:rgba(0,194,122,0.05)!important;border:1px solid rgba(0,194,122,0.15)!important;border-radius:var(--r-md)!important;}
    [data-testid="stError"]{background:rgba(240,69,90,0.05)!important;border:1px solid rgba(240,69,90,0.15)!important;border-radius:var(--r-md)!important;}

    /* === MISC === */
    [data-testid="stFileUploader"]{background:var(--s1)!important;border:2px dashed var(--b2)!important;border-radius:var(--r-lg)!important;}
    [data-testid="stFileUploader"] *{color:var(--t3)!important;}
    [data-testid="stChatInput"]>div{background:var(--s2)!important;border:1px solid var(--b2)!important;border-radius:var(--r-md)!important;}
    [data-testid="stChatMessage"]{background:var(--s1)!important;border:1px solid var(--b1)!important;border-radius:var(--r-lg)!important;}
    hr,[data-testid="stDivider"]{border-color:var(--b1)!important;margin:1rem 0!important;}
    [data-testid="metric-container"]{background:var(--s1)!important;border:1px solid var(--b1)!important;border-radius:var(--r-lg)!important;padding:14px 16px!important;}
    [data-testid="metric-container"] label{color:var(--t3)!important;font-size:9.5px!important;}
    [data-testid="stMetricValue"]{color:var(--t1)!important;font-weight:700!important;font-family:var(--mono)!important;}
    ::-webkit-scrollbar{width:3px;height:3px;} ::-webkit-scrollbar-track{background:transparent;} ::-webkit-scrollbar-thumb{background:var(--b2);border-radius:2px;}

    /* ════════════════════════════════════════
       CUSTOM COMPONENTS
    ════════════════════════════════════════ */

    /* Top bar */
    .vc-topbar{display:flex;align-items:center;gap:8px;padding:10px 0 12px;border-bottom:1px solid var(--b0);margin-bottom:16px;flex-wrap:wrap;}
    .vc-bc{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--t3);}
    .vc-bc-sep{color:var(--t4);font-size:10px;}
    .vc-bc-crumb{color:var(--t2);}
    .vc-bc-active{color:var(--t1)!important;font-weight:500;}
    .vc-tb-right{margin-left:auto;display:flex;align-items:center;gap:5px;}
    .vc-tb-div{width:1px;height:14px;background:var(--b1);margin:0 2px;display:inline-block;vertical-align:middle;}

    /* Status chip */
    .status-chip{display:inline-flex;align-items:center;gap:5px;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;}
    .sc-watch{background:rgba(245,166,35,0.07);border:1px solid rgba(245,166,35,0.2);color:var(--amber);}
    .sc-proceed{background:rgba(0,194,122,0.07);border:1px solid rgba(0,194,122,0.2);color:var(--green);}
    .sc-pass{background:rgba(240,69,90,0.07);border:1px solid rgba(240,69,90,0.2);color:var(--red);}
    .sc-pip{width:5px;height:5px;border-radius:50%;flex-shrink:0;display:inline-block;margin-right:2px;}

    /* Inline tab buttons (in topbar) */
    .tb-btn{display:inline-flex;align-items:center;height:26px;padding:0 10px;border-radius:var(--r-sm);border:1px solid transparent;background:transparent;color:var(--t3);font-size:11px;font-weight:500;font-family:var(--font);cursor:pointer;transition:all 0.1s;}
    .tb-btn:hover{background:var(--s3);color:var(--t1);border-color:var(--b2);}
    .tb-btn.active{background:var(--s3);color:var(--t1);border-color:var(--b2);}
    .tb-export{height:26px;padding:0 10px;border-radius:var(--r-sm);border:1px solid var(--b2);background:transparent;color:var(--t3);font-size:11px;font-weight:500;font-family:var(--font);cursor:pointer;}
    .tb-new{height:26px;padding:0 10px;border-radius:var(--r-sm);border:none;background:var(--blue);color:white;font-size:11px;font-weight:500;font-family:var(--font);cursor:pointer;}

    /* Tab row — the Streamlit button row acts as real tabs */
    .tab-row-wrap [data-testid="stHorizontalBlock"]{gap:4px!important;align-items:center!important;}
    .tab-row-wrap .stButton>button{height:30px!important;font-size:11px!important;font-weight:500!important;padding:0 14px!important;border-radius:var(--r-sm)!important;border:1px solid var(--b1)!important;background:transparent!important;color:var(--t3)!important;transition:all 0.1s!important;}
    .tab-row-wrap .stButton>button:hover{background:var(--s3)!important;color:var(--t1)!important;border-color:var(--b2)!important;}
    .tab-row-wrap .stButton>button[kind="primary"]{background:var(--s3)!important;color:var(--t1)!important;border-color:var(--b2)!important;}
    .tab-row-wrap .stButton>button[kind="secondary"]{background:transparent!important;color:var(--t3)!important;}

    /* Context strip */
    .context-strip{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:10px;}
    .ctx-tag{display:inline-flex;flex-direction:column;padding:4px 9px;border-radius:var(--r-sm);border:1px solid;}
    .ctx-tag-l{font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;opacity:0.45;margin-bottom:1px;}
    .ctx-tag-v{font-size:11px;font-weight:600;}
    .ctx-blue {background:rgba(76,142,255,0.06);border-color:rgba(76,142,255,0.16);color:#6ba3ff;}
    .ctx-vi   {background:rgba(124,106,247,0.06);border-color:rgba(124,106,247,0.16);color:#9d8fff;}
    .ctx-green{background:rgba(0,194,122,0.06);border-color:rgba(0,194,122,0.16);color:#00d488;}
    .ctx-amber{background:rgba(245,166,35,0.06);border-color:rgba(245,166,35,0.16);color:#f7b84b;}
    .ctx-red  {background:rgba(240,69,90,0.06);border-color:rgba(240,69,90,0.16);color:#f0455a;}
    .ctx-muted{background:rgba(255,255,255,0.02);border-color:var(--b1);color:var(--t2);}

    /* Alert banner */
    .alert-banner{display:flex;align-items:center;gap:9px;padding:8px 12px;border-radius:var(--r-sm);background:rgba(76,142,255,0.04);border:1px solid rgba(76,142,255,0.12);font-size:11px;color:#6ba3ff;line-height:1.4;margin-bottom:12px;}

    /* Card */
    .card{background:var(--s1);border:1px solid var(--b1);border-radius:var(--r-lg);overflow:hidden;margin-bottom:12px;}
    .card-h{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid var(--b0);}
    .card-h-title{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--t3);}
    .card-h-right{font-size:10px;color:var(--t4);}
    .card-h-action{font-size:10px;color:var(--blue);cursor:pointer;font-weight:500;}
    .card-b{padding:14px;}

    /* Decision card */
    .dec-card{background:var(--s1);border:1px solid var(--b1);border-radius:var(--r-lg);overflow:hidden;margin-bottom:12px;}
    .dec-accent{height:1px;}
    .dec-watch-a {background:linear-gradient(90deg,transparent,rgba(245,166,35,0.6) 30%,rgba(245,166,35,0.2) 70%,transparent);}
    .dec-proceed-a{background:linear-gradient(90deg,transparent,rgba(0,194,122,0.6) 30%,rgba(0,194,122,0.2) 70%,transparent);}
    .dec-pass-a  {background:linear-gradient(90deg,transparent,rgba(240,69,90,0.6) 30%,rgba(240,69,90,0.2) 70%,transparent);}
    .dec-body{padding:16px;}
    .dec-eyebrow{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--t3);margin-bottom:12px;}
    .dec-verdict{display:flex;align-items:center;gap:7px;margin-bottom:14px;}
    .dec-pip{width:7px;height:7px;border-radius:50%;flex-shrink:0;display:inline-block;}
    .dec-word{font-size:20px;font-weight:700;letter-spacing:-0.03em;}
    .dec-prob-num{font-size:40px;font-weight:800;font-family:var(--mono);letter-spacing:-0.04em;line-height:1;display:inline;}
    .dec-prob-unit{font-size:18px;font-weight:500;font-family:var(--mono);color:var(--t3);}
    .dec-prob-label{font-size:10px;color:var(--t3);margin-top:3px;}
    .dec-foot{display:flex;align-items:center;justify-content:space-between;padding-top:12px;border-top:1px solid var(--b0);margin-top:14px;}
    .dec-foot-l{font-size:10px;color:var(--t3);}
    .dec-foot-v{font-size:12px;font-weight:600;font-family:var(--mono);color:var(--t2);}

    /* KPI card */
    .kpi{background:var(--s1);border:1px solid var(--b1);border-radius:var(--r-lg);padding:14px 16px;display:flex;flex-direction:column;margin-bottom:12px;}
    .kpi-eye{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--t3);margin-bottom:8px;}
    .kpi-num{font-size:28px;font-weight:700;font-family:var(--mono);letter-spacing:-0.04em;line-height:1;margin-bottom:4px;}
    .kpi-denom{font-size:14px;font-weight:400;color:var(--t3);}
    .kpi-caption{font-size:10px;color:var(--t3);flex:1;}
    .kpi-track{height:2px;background:var(--s5);border-radius:1px;overflow:hidden;margin-top:12px;}
    .kpi-fill{height:100%;border-radius:1px;}

    /* Score breakdown */
    .sc-item{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--b0);}
    .sc-item:first-child{padding-top:0;}
    .sc-item:last-child{border-bottom:none;padding-bottom:0;}
    .sc-name{font-size:11px;font-weight:500;color:var(--t2);width:82px;flex-shrink:0;}
    .sc-track{flex:1;height:3px;background:var(--s4);border-radius:2px;overflow:hidden;}
    .sc-fill{height:100%;border-radius:2px;}
    .sc-val{font-size:11px;font-weight:600;font-family:var(--mono);width:22px;text-align:right;flex-shrink:0;}

    /* Drivers */
    .drv-group-label{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:var(--t4);margin:10px 0 6px;}
    .drv-group-label:first-child{margin-top:0;}
    .drv{display:flex;align-items:flex-start;gap:8px;padding:8px 9px;border-radius:var(--r-sm);margin-bottom:4px;}
    .drv-ico{width:15px;height:15px;border-radius:3px;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:800;flex-shrink:0;margin-top:1px;}
    .drv-pos{background:rgba(0,194,122,0.06);}
    .drv-pos .drv-ico{background:rgba(0,194,122,0.15);color:var(--green);}
    .drv-neg{background:rgba(245,166,35,0.05);}
    .drv-neg .drv-ico{background:rgba(245,166,35,0.15);color:var(--amber);}
    .drv-body{flex:1;min-width:0;}
    .drv-title{font-size:11px;font-weight:600;color:var(--t1);line-height:1.3;}
    .drv-desc{font-size:10px;color:var(--t3);margin-top:1px;line-height:1.4;}
    .drv-impact{font-size:10px;font-family:var(--mono);font-weight:600;flex-shrink:0;padding-top:1px;}

    /* Override flags */
    .flag{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid var(--b0);}
    .flag:last-child{border-bottom:none;}
    .flag-box{width:13px;height:13px;border-radius:3px;border:1px solid var(--b2);background:var(--s3);display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:800;flex-shrink:0;}
    .flag-box.on{background:rgba(76,142,255,0.15);border-color:rgba(76,142,255,0.35);color:var(--blue);}
    .flag-label{font-size:11px;color:var(--t2);flex:1;}
    .flag-val{font-size:10px;font-family:var(--mono);font-weight:600;}

    /* Metric pills */
    .mp-grid{display:flex;flex-wrap:wrap;gap:4px;}
    .mp{display:inline-flex;align-items:center;gap:3px;padding:3px 7px;border-radius:4px;font-size:10px;font-weight:500;}
    .mp-m{background:rgba(245,166,35,0.07);color:var(--amber);border:1px solid rgba(245,166,35,0.15);}
    .mp-h{background:rgba(0,194,122,0.07);color:var(--green);border:1px solid rgba(0,194,122,0.15);}

    /* Generate buttons */
    .gen{width:100%;padding:8px 10px;border-radius:var(--r-sm);border:1px solid var(--b1);background:var(--s2);color:var(--t2);font-size:11px;font-weight:500;font-family:var(--font);cursor:pointer;transition:all 0.1s;display:flex;align-items:center;gap:8px;text-align:left;margin-bottom:4px;}
    .gen:hover{border-color:var(--b3);background:var(--s3);color:var(--t1);}
    .gen-icon{width:19px;height:19px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:9px;flex-shrink:0;}
    .recalc-btn{margin-top:10px;width:100%;padding:7px;border-radius:var(--r-sm);background:var(--blue);border:none;color:white;font-size:11px;font-weight:600;font-family:var(--font);cursor:pointer;}

    /* Pipeline sidebar */
    .pl-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:8px;}
    .pl-cell{padding:7px 9px;border-radius:var(--r-sm);border:1px solid var(--b0);background:var(--s1);cursor:pointer;transition:all 0.1s;}
    .pl-cell.sel{background:rgba(76,142,255,0.06);border-color:rgba(76,142,255,0.2);}
    .pl-num{font-size:17px;font-weight:700;font-family:var(--mono);line-height:1;margin-bottom:2px;}
    .pl-lbl{font-size:9.5px;color:var(--t3);font-weight:500;}

    /* Deal cards */
    .deal-card{padding:9px 10px;border-radius:var(--r-sm);border:1px solid transparent;margin-bottom:2px;}
    .deal-card.sel{background:var(--s3);border-color:var(--b2);}
    .dc-row{display:flex;align-items:center;justify-content:space-between;}
    .dc-name{font-size:12px;font-weight:600;color:var(--t1);}
    .dc-prob{font-size:11px;font-weight:600;font-family:var(--mono);}
    .dc-sub{font-size:10px;color:var(--t3);margin:2px 0 5px;}
    .dc-bar{height:2px;background:var(--s5);border-radius:1px;overflow:hidden;}
    .dc-fill{height:100%;border-radius:1px;}

    /* Right panel */
    .rp-section{background:var(--s1);border:1px solid var(--b1);border-radius:var(--r-lg);padding:14px;margin-bottom:10px;}
    .rp-section-title{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--t3);margin-bottom:10px;}
    .rp-row{display:flex;align-items:flex-start;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--b0);}
    .rp-row:last-child{border-bottom:none;}
    .rp-row-label{font-size:10px;color:var(--t3);font-weight:500;}
    .rp-row-val{font-size:11px;font-weight:600;font-family:var(--mono);text-align:right;max-width:140px;word-break:break-word;}

    /* Cop chips */
    .cop-chip{display:flex;align-items:center;gap:7px;padding:7px 10px;border-radius:var(--r-sm);border:1px solid var(--b0);background:var(--s1);font-size:11px;color:var(--t2);cursor:pointer;transition:all 0.1s;margin-bottom:4px;font-weight:500;}
    .cop-chip:hover{border-color:var(--b2);background:var(--s2);color:var(--t1);}

    /* Benchmarks */
    .bench-row{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--b0);font-size:11px;}
    .bench-row:last-child{border-bottom:none;}
    .bl{color:var(--t3);} .bv{font-weight:700;} .ba{color:var(--t4);font-size:10px;}

    /* Urgency */
    .urgency-banner{display:flex;align-items:center;gap:9px;padding:9px 13px;border-radius:var(--r-sm);font-size:11px;font-weight:500;margin-bottom:12px;}

    /* Personalization notice */
    .pers-notice{display:flex;align-items:flex-start;gap:7px;padding:7px 11px;border-radius:var(--r-sm);background:rgba(124,106,247,0.05);border:1px solid rgba(124,106,247,0.15);font-size:11px;color:#9d8fff;margin-bottom:10px;line-height:1.4;}

    /* Misc */
    .sec-lbl{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:var(--t4);margin-bottom:8px;margin-top:4px;}
    .form-section-title{font-size:11px;font-weight:600;color:var(--t2);margin:12px 0 6px;letter-spacing:-0.01em;}
    .c-green{color:var(--green)!important;} .c-amber{color:var(--amber)!important;}
    .c-red{color:var(--red)!important;}     .c-blue{color:var(--blue)!important;}
    .c-dim{color:var(--t3)!important;}      .c-t2{color:var(--t2)!important;}
    .ff-mono{font-family:var(--mono)!important;}

    /* Overflow control */
    .main .block-container{overflow-x:hidden!important;}
    [data-testid="column"]{min-width:0!important;overflow:hidden!important;}
    .stNumberInput input,.stTextInput input{min-width:0!important;width:100%!important;}
    </style>
""", unsafe_allow_html=True)

# ========================================
# SESSION STATE INITIALIZATION
# ========================================

# Persistent user database using JSON file
import os as _os
USERS_DB_FILE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "users_db.json")

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

# Score adjustment: set of disabled flag titles (investor overrides)
if "disabled_neg_flags" not in st.session_state:
    st.session_state.disabled_neg_flags = set()

# Auto-login check using query params (runs once per session)
if not st.session_state.auto_login_checked:
    st.session_state.auto_login_checked = True
    query_params = st.query_params
    if "user" in query_params:
        username = query_params["user"]
        if username in st.session_state.users_db:
            st.session_state.current_user = username
            st.session_state.logged_in = True
            st.session_state.login_error = None
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
    """Try to auto-login from URL query param."""
    query_params = st.query_params
    if "user" in query_params:
        username = query_params["user"]
        if username in st.session_state.users_db:
            st.session_state.current_user = username
            st.session_state.logged_in = True
            st.session_state.login_error = None
            st.session_state.investor_prefs = st.session_state.users_db[username].get("investor_prefs")
            st.session_state.saved_deals = st.session_state.users_db[username].get("saved_deals", [])
            _rebuild_deals_by_status()
            return True
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

def _rebuild_deals_by_status():
    """Rebuild deals_by_status from saved_deals."""
    dbs = {"watchlist": [], "active": [], "reviewed": [], "passed": []}
    for d in st.session_state.saved_deals:
        s = d.get("status", "watchlist")
        if s in dbs:
            dbs[s].append(d)
    st.session_state.deals_by_status = dbs

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
# MAIN PAGE HEADER (topbar)
# ========================================
_company_bc = st.session_state.get("company") or "New Deal"
_list_bc = st.session_state.get("active_list", "active").capitalize()

# Build status chip
_chip_html = ""
if st.session_state.get("last_result"):
    _r = st.session_state.last_result
    _p = _r.get("prob_next_round", 0)
    _dec_raw, _ = get_investment_decision(_p)
    _chip_cls = {"Proceed": "sc-proceed", "Watch": "sc-watch", "Pass": "sc-pass"}.get(_dec_raw, "sc-watch")
    _pip_col = {"Proceed": "var(--green)", "Watch": "var(--amber)", "Pass": "var(--red)"}.get(_dec_raw, "var(--amber)")
    _chip_html = f'<span class="status-chip {_chip_cls}"><span class="sc-pip" style="background:{_pip_col};"></span>{_dec_raw} · {_p:.0%}</span>'

_t = st.session_state.active_tab
_tab_html = "".join([
    f'<span class="tb-btn{"  active" if _t==_n else ""}">{_n}</span>'
    for _n in ["Intake", "Analysis", "Copilot"]
])

# Topbar: breadcrumb + status chip only (no HTML tab buttons — real buttons below handle nav)
st.markdown(f"""
<div class="vc-topbar">
  <div class="vc-bc">
    <span class="vc-bc-crumb">Deals</span>
    <span class="vc-bc-sep">/</span>
    <span class="vc-bc-crumb">{_list_bc}</span>
    <span class="vc-bc-sep">/</span>
    <span class="vc-bc-active">{_company_bc}</span>
  </div>
  {_chip_html}
</div>
""", unsafe_allow_html=True)

# Tab + action row (single source of truth for navigation)
st.markdown('<div class="tab-row-wrap">', unsafe_allow_html=True)
_tb_c1, _tb_c2, _tb_c3, _sp, _exp_c, _new_c = st.columns([1, 1, 1, 5, 1, 1])
with _tb_c1:
    if st.button("Intake", use_container_width=True,
                 type="primary" if _t == "Intake" else "secondary", key="tab_intake"):
        scroll_to_top(); st.session_state.active_tab = "Intake"; st.rerun()
with _tb_c2:
    if st.button("Analysis", use_container_width=True,
                 type="primary" if _t == "Analysis" else "secondary", key="tab_analysis"):
        scroll_to_top(); st.session_state.active_tab = "Analysis"; st.rerun()
with _tb_c3:
    if st.button("Copilot", use_container_width=True,
                 type="primary" if _t == "Copilot" else "secondary", key="tab_copilot"):
        scroll_to_top(); st.session_state.active_tab = "Copilot"; st.rerun()
with _exp_c:
    if st.button("↓ Export", use_container_width=True, key="export_btn"):
        st.toast("Export coming soon!")
with _new_c:
    if st.button("+ New Deal", use_container_width=True, type="primary", key="new_deal_btn"):
        reset_deal(); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div style="border-bottom:1px solid var(--b0);margin:2px 0 16px;"></div>', unsafe_allow_html=True)

# ========================================
# SIDEBAR: AUTHENTICATION & INVESTOR PROFILE
# ========================================
with st.sidebar:
    # Brand header
    st.markdown("""
    <div style="padding:12px 14px 10px;border-bottom:1px solid var(--b0);">
        <div style="display:flex;align-items:center;gap:8px;">
            <svg width="22" height="22" viewBox="0 0 26 26" fill="none">
                <rect x="1" y="1" width="10" height="10" rx="2.5" fill="#4c8eff" opacity="0.9"/>
                <rect x="15" y="1" width="10" height="10" rx="2.5" fill="#7c6af7" opacity="0.7"/>
                <rect x="1" y="15" width="10" height="10" rx="2.5" fill="#7c6af7" opacity="0.7"/>
                <rect x="15" y="15" width="10" height="10" rx="2.5" fill="#4c8eff" opacity="0.4"/>
            </svg>
            <div>
                <div style="font-size:13px;font-weight:800;color:var(--t1);letter-spacing:-0.02em;line-height:1;">VCaaS</div>
                <div style="font-size:9.5px;color:var(--t4);margin-top:1px;">Deal Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Authentication section
    if not st.session_state.logged_in:
        st.markdown('<div style="padding:10px 14px 0;"><div class="sec-lbl">Sign In</div></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div style="padding:0 14px;">', unsafe_allow_html=True)
            auth_tab = st.radio("", ["Login", "Create Account"], horizontal=True, label_visibility="collapsed")
            username_input = st.text_input("Username", key="auth_username", placeholder="your username")
            password_input = st.text_input("Password", type="password", key="auth_password", placeholder="••••••••")
            if st.session_state.login_error:
                st.error(st.session_state.login_error)
            if auth_tab == "Login":
                if st.button("Login", use_container_width=True, type="primary"):
                    if username_input and password_input:
                        if login_user(username_input, password_input):
                            st.rerun()
                        else:
                            st.session_state.login_error = "Invalid username or password"
                            st.rerun()
                    else:
                        st.session_state.login_error = "Please enter username and password"
                        st.rerun()
            else:
                if st.button("Create Account", use_container_width=True, type="primary"):
                    if username_input and password_input:
                        if signup_user(username_input, password_input):
                            st.rerun()
                        else:
                            st.session_state.login_error = "Username already exists"
                            st.rerun()
                    else:
                        st.session_state.login_error = "Please provide username and password"
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # User is logged in — show avatar + name + action buttons
        _uname = st.session_state.current_user
        _initials = _uname[:2].upper()
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:10px 12px 6px;">
            <div style="width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#4c8eff,#7c6af7);display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:white;flex-shrink:0;">{_initials}</div>
            <div style="flex:1;min-width:0;overflow:hidden;">
                <div style="font-size:11px;font-weight:600;color:#eeeef2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_uname}</div>
                <div style="font-size:9px;color:#5a5e7a;">Logged in</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Compact action buttons row
        _sb1, _sb2 = st.columns(2)
        with _sb1:
            if st.button("Sign out", key="logout_btn", use_container_width=True):
                logout_user(); st.rerun()
        with _sb2:
            if st.button("Edit profile", key="edit_prefs_top", use_container_width=True):
                st.session_state.show_prefs_onboard = not st.session_state.show_prefs_onboard; st.rerun()
        st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.04);margin:6px 0 0;"></div>', unsafe_allow_html=True)

    # Investor Profile section (only shown when logged in)
    if st.session_state.logged_in:
        st.markdown('<div class="sec-lbl" style="padding:10px 14px 4px;">Investor Profile</div>', unsafe_allow_html=True)

    if st.session_state.investor_prefs:
        _ip = st.session_state.investor_prefs
        _min_arr = _ip.get('min_arr', 0) or 0
        _arr_fmt = f"${_min_arr/1_000_000:.1f}M" if _min_arr >= 1_000_000 else f"${_min_arr/1_000:.0f}K" if _min_arr >= 1_000 else f"${_min_arr}"
        st.markdown(f"""
        <div style="background:var(--s1);border:1px solid var(--b1);border-radius:var(--r-md);padding:10px 13px;margin:0 8px 10px;">
            <div style="font-size:12px;color:var(--t1);font-weight:600;margin-bottom:5px;">{_ip.get('investor_name','—')}</div>
            <div style="display:flex;flex-wrap:wrap;gap:3px;margin-bottom:4px;">
                <span style="font-size:10px;background:rgba(76,142,255,0.08);border:1px solid rgba(76,142,255,0.16);color:var(--blue);padding:1px 6px;border-radius:4px;">{_ip.get('preferred_stage','Any')}</span>
                <span style="font-size:10px;background:var(--s2);border:1px solid var(--b1);color:var(--t2);padding:1px 6px;border-radius:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:120px;">{_ip.get('preferred_sector','Any sector')}</span>
            </div>
            <div style="font-size:10px;color:var(--t3);">Min ARR {_arr_fmt}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:11px;color:var(--t3);padding:8px 14px 10px;">Set up your investor profile to personalize deal scoring.</div>', unsafe_allow_html=True)
    
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
        # Pipeline counts
        wl_n = len([d for d in st.session_state.saved_deals if d.get("status") == "watchlist"])
        ac_n = len([d for d in st.session_state.saved_deals if d.get("status") == "active"])
        rv_n = len([d for d in st.session_state.saved_deals if d.get("status") == "reviewed"])
        ps_n = len([d for d in st.session_state.saved_deals if d.get("status") == "passed"])
        _sel = st.session_state.active_list

        st.markdown(f"""
        <div style="padding:10px 12px 8px;">
          <div class="sec-lbl">Pipeline</div>
          <div class="pl-grid">
            <div class="pl-cell {'sel' if _sel=='watchlist' else ''}">
              <div class="pl-num {'c-dim' if wl_n==0 else ''}">{wl_n}</div>
              <div class="pl-lbl">📌 Watchlist</div>
            </div>
            <div class="pl-cell {'sel' if _sel=='active' else ''}">
              <div class="pl-num {'c-amber' if ac_n>0 else 'c-dim'}">{ac_n}</div>
              <div class="pl-lbl">⚡ Active</div>
            </div>
            <div class="pl-cell {'sel' if _sel=='reviewed' else ''}">
              <div class="pl-num {'c-blue' if rv_n>0 else 'c-dim'}">{rv_n}</div>
              <div class="pl-lbl">📋 Reviewed</div>
            </div>
            <div class="pl-cell {'sel' if _sel=='passed' else ''}">
              <div class="pl-num c-dim">{ps_n}</div>
              <div class="pl-lbl">✕ Passed</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # List selector — compact radio row
        _list_choice = st.radio(
            "list_filter", ["Watchlist", "Active", "Reviewed", "Passed"],
            index=["watchlist","active","reviewed","passed"].index(st.session_state.active_list),
            horizontal=True, label_visibility="collapsed", key="sidebar_list_radio"
        )
        if _list_choice.lower() != st.session_state.active_list:
            st.session_state.active_list = _list_choice.lower()
            st.rerun()

        # Search
        search_filter = st.text_input(
            "Search",
            value=st.session_state.deal_filters["search"],
            placeholder="Search deals…",
            label_visibility="collapsed",
            key="sidebar_search"
        )
        st.session_state.deal_filters["search"] = search_filter

        # Deal list
        filtered_deals = get_filtered_deals(st.session_state.active_list)
        st.markdown(f'<div style="padding:6px 14px 4px;font-size:9.5px;font-weight:600;color:var(--t4);text-transform:uppercase;letter-spacing:0.08em;">{len(filtered_deals)} in {st.session_state.active_list.capitalize()}</div>', unsafe_allow_html=True)

        if filtered_deals:
            for _deal in filtered_deals[:20]:
                _dc_col = {"Proceed": "#00c27a", "Watch": "#f5a623", "Pass": "#f0455a"}.get(_deal.get("decision"), "#5a5e7a")
                _pct_raw = _deal.get('prob_next_round', 0)
                _pct_str = f"{_pct_raw:.0%}"
                _pct_w = f"{int(_pct_raw*100)}%"
                _is_active = (_deal.get("company") == (st.session_state.get("company") or ""))
                _sel_cls = "sel" if _is_active else ""

                st.markdown(f"""
                <div class="deal-card {_sel_cls}" style="margin:0 8px 2px;">
                    <div class="dc-row">
                        <span class="dc-name">{_deal['company']}</span>
                        <span class="dc-prob" style="color:{_dc_col};">{_pct_str}</span>
                    </div>
                    <div class="dc-sub">{_deal.get('stage','—')} · {_deal.get('sector','')[:24]}</div>
                    <div class="dc-bar"><div class="dc-fill" style="width:{_pct_w};background:{_dc_col};"></div></div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Open {_deal['company']} →", key=f"load_{_deal['id']}", use_container_width=True):
                    load_deal(_deal)
                    st.session_state.active_tab = "Analysis"
                    st.toast(f"Loaded {_deal['company']}")
                    st.rerun()
        else:
            st.markdown(f'<div style="font-size:11px;color:var(--t4);padding:1rem 14px;text-align:center;">No deals in {st.session_state.active_list.capitalize()}</div>', unsafe_allow_html=True)

    elif st.session_state.logged_in:
        st.markdown('<div style="padding:10px 12px 8px;"><div class="sec-lbl">Pipeline</div><div style="font-size:11px;color:var(--t4);padding:1rem 0;text-align:center;">Run analysis and save your first deal!</div></div>', unsafe_allow_html=True)

# ========================================
# TAB CONTENT
# ========================================

# Require login to access main content
if not st.session_state.logged_in:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4rem 2rem;text-align:center;">
        <div style="font-size:28px;margin-bottom:12px;">🔐</div>
        <div style="font-size:14px;font-weight:600;color:var(--t1);margin-bottom:6px;">Sign in to access VCaaS</div>
        <div style="font-size:12px;color:var(--t3);">Use the sidebar to login or create an account.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Show content based on active_tab
if st.session_state.active_tab == "Intake":
    st.markdown('<div style="font-size:13px;font-weight:600;color:var(--t1);margin-bottom:12px;">Documents & Data</div>', unsafe_allow_html=True)
    
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
                        # Auto-apply extracted fields to session state
                        for k in ["company", "stage", "sector", "raise_amount_usd", "arr_usd", "growth_rate_pct", "runway_months", "notes"]:
                            if k in st.session_state.extracted and st.session_state.extracted[k] is not None:
                                st.session_state[k] = st.session_state.extracted[k]
                        if st.session_state.founder_email:
                            st.toast(f"📧 Contact found: {st.session_state.founder_email}")
                        st.rerun()
                    else:
                        st.warning("⚠️ Could not extract fields. Review document quality.")
    
    st.divider()
    
    # Extraction preview
    if st.session_state.extracted:
        st.markdown('<div class="form-section-title">🔍 Extracted Data Preview</div>', unsafe_allow_html=True)
        
        with st.expander("View JSON", expanded=False):
            st.code(json.dumps(st.session_state.extracted, indent=2), language="json")
        
    st.divider()
    
    # Deal fields
    st.markdown('<div class="form-section-title">📋 Deal Details</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="small")
    
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
    
    col1, col2 = st.columns(2, gap="small")
    
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
                st.session_state.disabled_neg_flags = set()  # reset overrides on new analysis
                
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

        # Decision colors — use actual hex, not CSS variables (CSS vars don't resolve in Streamlit inline styles)
        _CLR = {"Proceed": "#00c27a", "Watch": "#f5a623", "Pass": "#f0455a"}
        d_color = _CLR[decision]
        fit_color = "#00c27a" if fit_score >= 70 else "#f5a623" if fit_score >= 40 else "#f0455a"
        q_color  = "#00c27a" if deal_quality >= 70 else "#f5a623" if deal_quality >= 50 else "#f0455a"

        # ── CONTEXT STRIP ──────────────────────────────────────────────
        _stage_ctx = "ctx-blue" if deal.get('stage','') in ("Seed","Pre-Seed") else "ctx-vi" if deal.get('stage','') == "Series A" else "ctx-green"
        _arr_ctx = "ctx-green" if arr_val >= 500_000 else "ctx-amber" if arr_val >= 100_000 else "ctx-muted"
        _run_ctx = "ctx-green" if runway >= 18 else "ctx-amber" if runway >= 12 else "ctx-red"
        _growth_ctx = "ctx-green" if growth_pct > 10 else "ctx-amber" if growth_pct > 0 else "ctx-red"
        st.markdown(f"""
        <div class="context-strip">
            <div class="ctx-tag {_stage_ctx}"><div class="ctx-tag-l">Stage</div><div class="ctx-tag-v">{deal.get('stage','—')}</div></div>
            <div class="ctx-tag ctx-muted" style="max-width:180px;"><div class="ctx-tag-l">Sector</div><div class="ctx-tag-v" style="font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{deal.get('sector','—')}</div></div>
            <div class="ctx-tag {_arr_ctx}"><div class="ctx-tag-l">ARR</div><div class="ctx-tag-v">{arr_display}</div></div>
            <div class="ctx-tag ctx-amber"><div class="ctx-tag-l">Raising</div><div class="ctx-tag-v">{raise_display}</div></div>
            <div class="ctx-tag {_run_ctx}"><div class="ctx-tag-l">Runway</div><div class="ctx-tag-v">{runway} mo</div></div>
            <div class="ctx-tag {_growth_ctx}"><div class="ctx-tag-l">Growth</div><div class="ctx-tag-v">{growth_pct:.0f}%</div></div>
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

            _dec_accent = {"Proceed": "dec-proceed-a", "Watch": "dec-watch-a", "Pass": "dec-pass-a"}[decision]
            with c1:
                st.markdown(
                    f'<div class="dec-card">'
                    f'<div class="dec-accent {_dec_accent}"></div>'
                    f'<div class="dec-body">'
                    f'<div class="dec-eyebrow">Investment Decision</div>'
                    f'<div class="dec-verdict">'
                    f'<span class="dec-pip" style="background:{d_color}"></span>'
                    f'<span class="dec-word" style="color:{d_color}">{decision}</span>'
                    f'</div>'
                    f'<div><span class="dec-prob-num" style="color:{d_color}">{int(prob*100)}</span>'
                    f'<span class="dec-prob-unit">%</span></div>'
                    f'<div class="dec-prob-label">next-round probability</div>'
                    f'<div class="dec-foot">'
                    f'<span class="dec-foot-l">Model confidence</span>'
                    f'<span class="dec-foot-v">{int(confidence*100)}%</span>'
                    f'</div></div></div>',
                    unsafe_allow_html=True
                )

            with c2:
                sector_note = "Sector outside thesis" if any("sector" in p.lower() for p in (personalization_applied or [])) else "Sector match"
                st.markdown(
                    f'<div class="kpi">'
                    f'<div class="kpi-eye">Investor Fit</div>'
                    f'<div><span class="kpi-num" style="color:{fit_color}">{fit_score}</span>'
                    f'<span class="kpi-denom">/100</span></div>'
                    f'<div class="kpi-caption">{sector_note}</div>'
                    f'<div class="kpi-track" style="margin-top:8px">'
                    f'<div class="kpi-fill" style="width:{fit_score}%;background:{fit_color}"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with c3:
                st.markdown(
                    f'<div class="kpi">'
                    f'<div class="kpi-eye">Deal Quality</div>'
                    f'<div><span class="kpi-num" style="color:{q_color}">{deal_quality:.0f}</span>'
                    f'<span class="kpi-denom">/100</span></div>'
                    f'<div class="kpi-caption">{missing_count}/8 metrics missing · ~{time_to_diligence}d diligence</div>'
                    f'<div class="kpi-track" style="margin-top:8px">'
                    f'<div class="kpi-fill" style="width:{deal_quality:.0f}%;background:{q_color}"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # ── SCORE BREAKDOWN + WHY THIS SCORE ───────────────────────
            sb_col, why_col = st.columns(2)

            with sb_col:
                _COLOR_G = "#00c27a"; _COLOR_A = "#f5a623"; _COLOR_R = "#f0455a"
                bars_html = ""
                for cat, score in category_scores.items():
                    pct = min(100, score / 10.0 * 100)
                    clr = _COLOR_G if score >= 7 else _COLOR_A if score >= 5 else _COLOR_R
                    lbl = (cat[:10] + "…") if len(cat) > 11 else cat
                    bars_html += (
                        f'<div class="sc-item">'
                        f'<span class="sc-name">{lbl}</span>'
                        f'<div class="sc-track"><div class="sc-fill" style="width:{pct:.0f}%;background:{clr}"></div></div>'
                        f'<span class="sc-val" style="color:{clr}">{score:.1f}</span>'
                        f'</div>'
                    )
                n_cats = len(category_scores)
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-h"><span class="card-h-title">Score Breakdown</span>'
                    f'<span class="card-h-right">{n_cats} categories</span></div>'
                    f'<div class="card-b">{bars_html}</div></div>',
                    unsafe_allow_html=True
                )

            with why_col:
                import re as _re
                def _drv_item(drv, is_pos):
                    arrow = "↑" if is_pos else "↓"
                    css = "drv-pos" if is_pos else "drv-neg"
                    clr = "#00c27a" if is_pos else "#f5a623"
                    sign = "+" if is_pos else "−"
                    m = _re.search(r'(\d+)', str(drv.get('impact', '5%')))
                    delta = m.group(1) if m else "5"
                    title = drv.get('title', '')[:48]
                    desc = drv.get('explanation', '')[:90]
                    if len(drv.get('explanation', '')) > 90:
                        desc += "…"
                    return (
                        f'<div class="drv {css}">'
                        f'<div class="drv-ico">{arrow}</div>'
                        f'<div class="drv-body">'
                        f'<div class="drv-title">{title}</div>'
                        f'<div class="drv-desc">{desc}</div>'
                        f'</div>'
                        f'<span class="drv-impact" style="color:{clr}">{sign}{delta}%</span>'
                        f'</div>'
                    )
                pos_html = "".join(_drv_item(d, True) for d in result.get("drivers_pos_detailed", [])[:2])
                neg_html = "".join(_drv_item(d, False) for d in result.get("drivers_neg_detailed", [])[:2])
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-h"><span class="card-h-title">Why This Score</span></div>'
                    f'<div class="card-b">'
                    f'<div class="drv-group-label">Positive Signals</div>{pos_html}'
                    f'<div class="drv-group-label" style="margin-top:10px">Risk Factors</div>{neg_html}'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

            # ── NEW: STAGE BENCHMARKS ───────────────────────────────────
            _stage = deal.get('stage', 'Seed')
            _bench = {
                "Pre-Seed": {"ARR": "$100K", "Growth": "15%", "Runway": "18 mo"},
                "Seed":     {"ARR": "$500K", "Growth": "20%", "Runway": "18 mo"},
                "Series A": {"ARR": "$2M",   "Growth": "30%", "Runway": "24 mo"},
                "Series B+":{"ARR": "$10M",  "Growth": "50%", "Runway": "24 mo"},
            }.get(_stage, {"ARR": "$500K", "Growth": "20%", "Runway": "18 mo"})

            _arr_vs = "above" if arr_val >= 500_000 else "below"
            _ac = "#00c27a"; _am = "#f5a623"; _ar = "#f0455a"
            _arr_color   = _ac if _arr_vs == "above" else _ar
            _growth_color = _ac if growth_pct >= 20 else _ar if growth_pct < 10 else _am
            _run_color    = _ac if runway >= 18 else _ar if runway < 12 else _am

            st.markdown(
                f'<div class="card">'
                f'<div class="card-h"><span class="card-h-title">Stage Benchmarks vs. {_stage} Median</span></div>'
                f'<div class="card-b">'
                f'<div class="bench-row"><span class="bl">ARR</span>'
                f'<span class="bv" style="color:{_arr_color}">{arr_display}</span>'
                f'<span class="ba">median {_bench["ARR"]}</span></div>'
                f'<div class="bench-row"><span class="bl">Growth MoM</span>'
                f'<span class="bv" style="color:{_growth_color}">{growth_pct:.0f}%</span>'
                f'<span class="ba">median {_bench["Growth"]}</span></div>'
                f'<div class="bench-row"><span class="bl">Runway</span>'
                f'<span class="bv" style="color:{_run_color}">{runway} mo</span>'
                f'<span class="ba">median {_bench["Runway"]}</span></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

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

            st.markdown(
                f'<div class="urgency-banner" style="background:{urg_bg};border:1px solid {urg_bd};color:{urg_tc}">{urg_msg}</div>',
                unsafe_allow_html=True
            )

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

            st.markdown('<div style="border-top:1px solid var(--b1);margin:1.25rem 0 1rem;"></div>', unsafe_allow_html=True)

            # ── VIBE CHECK / SCORE ADJUSTMENT ────────────────────────────
            _neg_flags_main = result.get("drivers_neg_detailed", [])
            if _neg_flags_main:
                import re as _re3
                st.markdown(
                    '<div class="card"><div class="card-h">'
                    '<span class="card-h-title">Vibe Check — Score Adjustment</span>'
                    '<span class="card-h-right">Override flags with qualitative context</span>'
                    '</div><div class="card-b">',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<div style="font-size:10px;color:#5a5e7a;margin-bottom:10px;line-height:1.5;">'
                    'Uncheck any negative flag you can explain with off-model context '
                    '(e.g. imminent contract, insider round, team background verified). '
                    'The adjusted probability recalculates instantly.</div>',
                    unsafe_allow_html=True
                )
                _base_prob_main = result.get("prob_next_round", 0)
                _adj_delta_main = 0.0
                for _fi2, _flag2 in enumerate(_neg_flags_main):
                    _ft2 = _flag2.get("title", f"Flag {_fi2}")
                    _fe2 = _flag2.get("explanation", "")
                    _fi2_imp = _flag2.get("impact", "")
                    _fm2 = _re3.search(r'(\d+(?:\.\d+)?)', str(_fi2_imp))
                    _fn2 = float(_fm2.group(1)) if _fm2 else 2.0
                    _key2 = f"vibe_flag_{_fi2}"
                    _is_dis2 = _ft2 in st.session_state.disabled_neg_flags
                    _chk2 = st.checkbox(
                        f"**{_ft2}** — _{_fe2[:80]}{'…' if len(_fe2)>80 else ''}_  \n"
                        f"{'~~' if _is_dis2 else ''}Impact: −{_fn2:.0f}% probability{'~~' if _is_dis2 else ''}",
                        value=not _is_dis2, key=_key2
                    )
                    if _chk2 and _ft2 in st.session_state.disabled_neg_flags:
                        st.session_state.disabled_neg_flags.discard(_ft2); st.rerun()
                    elif not _chk2 and _ft2 not in st.session_state.disabled_neg_flags:
                        st.session_state.disabled_neg_flags.add(_ft2); st.rerun()
                    if _ft2 in st.session_state.disabled_neg_flags:
                        _adj_delta_main += _fn2 / 100.0

                st.markdown('</div></div>', unsafe_allow_html=True)

                if st.session_state.disabled_neg_flags:
                    _adj_p2 = min(0.99, _base_prob_main + _adj_delta_main)
                    _adj_dec2, _ = get_investment_decision(_adj_p2)
                    _adj_clr2 = {"Proceed": "#00c27a", "Watch": "#f5a623", "Pass": "#f0455a"}[_adj_dec2]
                    _base_clr2 = {"Proceed": "#00c27a", "Watch": "#f5a623", "Pass": "#f0455a"}[decision]
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:16px;background:rgba(76,142,255,0.05);'
                        f'border:1px solid rgba(76,142,255,0.15);border-radius:10px;padding:12px 16px;margin-top:4px;">'
                        f'<div><div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#5a5e7a;margin-bottom:2px;">Base Score</div>'
                        f'<div style="font-size:28px;font-weight:800;font-family:\'Geist Mono\',monospace;color:{_base_clr2};line-height:1">{int(_base_prob_main*100)}%</div>'
                        f'<div style="font-size:10px;color:{_base_clr2}">{decision}</div></div>'
                        f'<div style="font-size:18px;color:#2e3248">→</div>'
                        f'<div><div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#5a5e7a;margin-bottom:2px;">Adjusted Score</div>'
                        f'<div style="font-size:28px;font-weight:800;font-family:\'Geist Mono\',monospace;color:{_adj_clr2};line-height:1">{int(_adj_p2*100)}%</div>'
                        f'<div style="font-size:10px;color:{_adj_clr2}">{_adj_dec2}</div></div>'
                        f'<div style="margin-left:auto;font-size:11px;color:#5a5e7a;">'
                        f'{len(st.session_state.disabled_neg_flags)} flag{"s" if len(st.session_state.disabled_neg_flags)>1 else ""} overridden</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("↺ Reset all overrides", key="vibe_reset_main", use_container_width=True):
                        st.session_state.disabled_neg_flags = set(); st.rerun()

            st.markdown('<div style="border-top:1px solid var(--b1);margin:1.25rem 0 1rem;"></div>', unsafe_allow_html=True)

            # ── GENERATE CONTENT ─────────────────────────────────────────
            st.markdown('<div class="sec-lbl">Generate Content</div>', unsafe_allow_html=True)
            gc1, gc2 = st.columns(2)
            gc3_full = st.container()

            with gc1:
                if st.button("❓ Diligence Qs", use_container_width=True):
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

            with gc3_full:
                if st.button("📝 Generate IC Memo", use_container_width=True):
                    client = get_openai_client()
                    if client:
                        with st.spinner("Drafting memo..."):
                            st.session_state.ic_memo = generate_ic_memo(deal, result, client)
                        st.rerun()

            # Display generated content
            if st.session_state.founder_questions:
                st.markdown('<div style="border-top:1px solid var(--b1);margin:1.25rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**❓ Diligence Questions**")
                st.write(st.session_state.founder_questions)

            if st.session_state.founder_followup:
                st.markdown('<div style="border-top:1px solid var(--b1);margin:1.25rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**✉️ Follow-up Email**")
                st.code(st.session_state.founder_followup, language=None)
                if st.session_state.founder_email:
                    import urllib.parse
                    mailto_link = f"mailto:{st.session_state.founder_email}?subject={urllib.parse.quote('Follow-up: ' + deal.get('company',''))}&body={urllib.parse.quote(st.session_state.founder_followup)}"
                    st.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration:none;"><button style="padding:7px 14px;background:var(--blue);color:white;border:none;border-radius:var(--r-sm);cursor:pointer;font-weight:600;font-size:11px;font-family:var(--font);">📧 Open in Email Client</button></a>', unsafe_allow_html=True)
                else:
                    st.caption("No contact email found in deck — add it to Notes for mailto link")

            if st.session_state.ic_memo:
                st.markdown('<div style="border-top:1px solid var(--b1);margin:1.25rem 0;"></div>', unsafe_allow_html=True)
                st.markdown("**📝 Investment Committee Memo**")
                st.write(st.session_state.ic_memo)

        # ── RIGHT PANEL ───────────────────────────────────────────────────
        with right_col:

            # Deal Info card
            growth_vc = "var(--green)" if growth_pct > 10 else "var(--red)" if growth_pct <= 0 else "var(--amber)"
            runway_vc = "var(--green)" if runway >= 18 else "var(--amber)" if runway >= 12 else "var(--red)"

            st.markdown(f"""
            <div class="rp-section">
                <div class="rp-section-title">Deal Info</div>
                <div class="rp-row"><span class="rp-row-label">Company</span><span class="rp-row-val c-blue">{deal.get('company','—')}</span></div>
                <div class="rp-row"><span class="rp-row-label">Stage</span><span class="rp-row-val c-blue">{deal.get('stage','—')}</span></div>
                <div class="rp-row"><span class="rp-row-label">ARR</span><span class="rp-row-val c-green">{arr_display}</span></div>
                <div class="rp-row"><span class="rp-row-label">Raising</span><span class="rp-row-val">{raise_display}</span></div>
                <div class="rp-row"><span class="rp-row-label">Growth MoM</span><span class="rp-row-val" style="color:{growth_vc};">{growth_pct:.0f}%</span></div>
                <div class="rp-row"><span class="rp-row-label">Runway</span><span class="rp-row-val" style="color:{runway_vc};">{runway} mo</span></div>
                <div class="rp-row"><span class="rp-row-label">Sector</span><span class="rp-row-val c-t2" style="font-size:10px;">{deal.get('sector','—')}</span></div>
                <div class="rp-row"><span class="rp-row-label">Updated</span><span class="rp-row-val c-dim">{datetime.now().strftime('%b %d · %H:%M')}</span></div>
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

            # ── SCORE ADJUSTMENT PANEL ───────────────────────────────────
            st.markdown('<div style="border-top:1px solid var(--b1);margin:12px 0 10px;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-lbl">Score Adjustment</div>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:10px;color:var(--t3);margin-bottom:8px;line-height:1.4;">'
                'Uncheck any flag you can explain with off-model context (e.g. imminent contract, insider round). '
                'The score recalculates instantly.</div>',
                unsafe_allow_html=True
            )

            _neg_flags = result.get("drivers_neg_detailed", [])
            _base_prob = result.get("prob_next_round", 0)
            _adj_delta = 0.0
            _any_override = False

            import re as _re2
            for _fi, _flag in enumerate(_neg_flags):
                _ftitle = _flag.get("title", f"Flag {_fi}")
                _fexpl  = _flag.get("explanation", "")[:80] + ("…" if len(_flag.get("explanation","")) > 80 else "")
                _fimp   = _flag.get("impact", "")
                _fkey   = f"flag_override_{_fi}"

                # Parse impact number
                _fm = _re2.search(r'(-?\d+(?:\.\d+)?)', str(_fimp))
                _fnum = float(_fm.group(1)) if _fm else -2.0

                _is_disabled = _ftitle in st.session_state.disabled_neg_flags
                _enabled = not _is_disabled

                col_chk, col_txt = st.columns([1, 8])
                with col_chk:
                    _checked = st.checkbox("", value=_enabled, key=_fkey, label_visibility="collapsed")
                with col_txt:
                    _lbl_color = "var(--t2)" if _checked else "var(--t4)"
                    _imp_color = "#f0455a" if _checked else "var(--t4)"
                    _pct_str = f"{abs(_fnum):.0f}%"
                    st.markdown(
                        f'<div style="padding:3px 0;">'
                        f'<div style="font-size:11px;font-weight:500;color:{_lbl_color};line-height:1.3">{_ftitle}</div>'
                        f'<div style="font-size:10px;color:var(--t3);margin-top:1px;">{_fexpl}</div>'
                        f'<div style="font-size:9.5px;color:{_imp_color};font-weight:600;margin-top:2px;">impact: −{_pct_str}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                # Handle toggle changes
                if _checked and _ftitle in st.session_state.disabled_neg_flags:
                    st.session_state.disabled_neg_flags.discard(_ftitle)
                    st.rerun()
                elif not _checked and _ftitle not in st.session_state.disabled_neg_flags:
                    st.session_state.disabled_neg_flags.add(_ftitle)
                    st.rerun()

                if _ftitle in st.session_state.disabled_neg_flags:
                    _adj_delta += abs(_fnum) / 100.0
                    _any_override = True

            # Show adjusted score if any overrides active
            if _any_override:
                _adj_prob = min(0.99, _base_prob + _adj_delta)
                _adj_pct = int(_adj_prob * 100)
                _adj_dec, _ = get_investment_decision(_adj_prob)
                _adj_clr = {"Proceed": "#00c27a", "Watch": "#f5a623", "Pass": "#f0455a"}[_adj_dec]
                st.markdown(
                    f'<div style="background:rgba(76,142,255,0.06);border:1px solid rgba(76,142,255,0.18);'
                    f'border-radius:8px;padding:10px 12px;margin-top:8px;">'
                    f'<div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;'
                    f'color:var(--t3);margin-bottom:4px;">Adjusted Score</div>'
                    f'<div style="display:flex;align-items:baseline;gap:6px;">'
                    f'<span style="font-size:28px;font-weight:800;font-family:var(--mono);color:{_adj_clr}">{_adj_pct}%</span>'
                    f'<span style="font-size:11px;color:var(--t3);">vs base {int(_base_prob*100)}%</span>'
                    f'</div>'
                    f'<div style="font-size:10px;color:{_adj_clr};font-weight:600;margin-top:2px;">{_adj_dec}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("↺ Reset all flags", key="reset_flags", use_container_width=True):
                    st.session_state.disabled_neg_flags = set()
                    st.rerun()

            # Quick Copilot
            st.markdown('<div style="border-top:1px solid var(--b1);margin:12px 0 10px;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-lbl">Quick Copilot</div>', unsafe_allow_html=True)

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
