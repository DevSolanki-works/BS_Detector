# app.py — ContractGuard: Professional UI Edition
# streamlit run app.py

import streamlit as st
import time

from src.llm_handler import analyse_contract, get_available_models, get_model_label
from src.doc_parser import extract_text
from src.classifier import classify_document, load_model, load_labels

# ── Session state ─────────────────────────────────────────────────────────────
for key, val in {"sample_loaded": False, "sample_text": "", "result": None, "elapsed": 0}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ContractGuard · Legal BS Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, body { font-family: 'Inter', sans-serif; }

/* ── App background ── */
[data-testid="stAppViewContainer"] { background: #07090f; }
[data-testid="stMain"] { background: #07090f; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0d1117 100%);
    border-right: 1px solid #1e2736;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem; }
.block-container { padding-top: 1.5rem !important; max-width: 1400px; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0f1923 0%, #111827 60%, #0f1923 100%);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3);
    border-radius: 99px; padding: 4px 14px;
    font-size: 0.75rem; font-weight: 600; color: #60a5fa;
    letter-spacing: 0.06em; margin-bottom: 1rem;
}
.hero-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #3b82f6; animation: pulse-dot 2s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.4} }
.hero h1 { font-size: 2.4rem; font-weight: 700; color: #f0f6ff; margin: 0 0 0.5rem; letter-spacing: -0.02em; }
.hero h1 span { color: #3b82f6; }
.hero-sub { font-size: 1rem; color: #6b7a93; margin: 0 0 1.5rem; line-height: 1.6; }
.hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; }
.hero-stat { display: flex; flex-direction: column; }
.hero-stat-val { font-size: 1.3rem; font-weight: 700; color: #f0f6ff; }
.hero-stat-label { font-size: 0.75rem; color: #6b7a93; margin-top: 2px; }

/* ── Sidebar elements ── */
.sidebar-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; }
.sidebar-logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.sidebar-logo-text { font-size: 1.1rem; font-weight: 700; color: #f0f6ff; }
.sidebar-logo-sub { font-size: 0.72rem; color: #6b7a93; }
.sidebar-section { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; color: #4a5568; text-transform: uppercase; margin: 1.2rem 0 0.5rem; }
.stat-pill {
    display: flex; align-items: center; gap: 8px;
    background: #0f1923; border: 1px solid #1e2736;
    border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
}
.stat-pill-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.stat-pill-text { font-size: 0.8rem; color: #8899aa; }

/* ── Input area ── */
.input-card {
    background: #0d1117; border: 1px solid #1e2736;
    border-radius: 16px; padding: 0.5rem 0;
    margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 8px !important;
    color: #6b7a93 !important; font-size: 0.85rem !important;
    padding: 6px 16px !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #1e2736 !important; color: #f0f6ff !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTextArea textarea {
    background: #0d1117 !important; border: 1px solid #1e2736 !important;
    border-radius: 12px !important; color: #d0dae8 !important;
    font-size: 0.9rem !important; line-height: 1.7 !important;
    resize: vertical !important;
}
.stTextArea textarea:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important; }

/* ── Scan button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    border: none !important; border-radius: 12px !important;
    font-size: 1rem !important; font-weight: 600 !important;
    letter-spacing: 0.02em !important; padding: 0.7rem 2rem !important;
    color: white !important; box-shadow: 0 4px 20px rgba(59,130,246,0.25) !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 28px rgba(59,130,246,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Verdict banner ── */
.verdict-wrap { border-radius: 16px; padding: 1.4rem 1.8rem; margin: 1.2rem 0; display: flex; align-items: center; gap: 1.2rem; }
.verdict-SIGN     { background: linear-gradient(135deg,#052e16,#0d4429); border: 1px solid #166534; }
.verdict-NEGOTIATE{ background: linear-gradient(135deg,#1c1400,#2d2a0e); border: 1px solid #854d0e; }
.verdict-DONOT    { background: linear-gradient(135deg,#2d0000,#490202); border: 1px solid #991b1b; }
.verdict-icon { font-size: 2.2rem; flex-shrink: 0; }
.verdict-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }
.verdict-text { font-size: 1.3rem; font-weight: 700; margin: 0 0 4px; }
.verdict-reason { font-size: 0.88rem; opacity: 0.8; line-height: 1.5; }
.verdict-SIGN .verdict-label, .verdict-SIGN .verdict-text { color: #4ade80; }
.verdict-SIGN .verdict-reason { color: #86efac; }
.verdict-NEGOTIATE .verdict-label, .verdict-NEGOTIATE .verdict-text { color: #fbbf24; }
.verdict-NEGOTIATE .verdict-reason { color: #fde68a; }
.verdict-DONOT .verdict-label, .verdict-DONOT .verdict-text { color: #f87171; }
.verdict-DONOT .verdict-reason { color: #fca5a5; }

/* ── Metric cards ── */
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1.2rem 0; }
.metric-card {
    background: #0d1117; border: 1px solid #1e2736;
    border-radius: 14px; padding: 1rem 1.2rem;
}
.metric-card-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #4a5568; margin-bottom: 6px; }
.metric-card-val { font-size: 1.6rem; font-weight: 700; color: #f0f6ff; }
.metric-card-sub { font-size: 0.75rem; color: #6b7a93; margin-top: 3px; }

/* ── Risk badge ── */
.risk-LOW      { color:#4ade80; }
.risk-MEDIUM   { color:#fbbf24; }
.risk-HIGH     { color:#fb923c; }
.risk-CRITICAL { color:#f87171; }

/* ── Section card ── */
.section-card {
    background: #0d1117; border: 1px solid #1e2736;
    border-radius: 16px; padding: 1.4rem 1.6rem; height: 100%;
}
.section-title { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; }
.section-title-icon { font-size: 1rem; }
.section-title-text { font-size: 0.95rem; font-weight: 600; color: #c8d6e8; letter-spacing: -0.01em; }
.section-divider { border: none; border-top: 1px solid #1e2736; margin: 1rem 0; }

/* ── Flag cards ── */
.flag-item {
    border-radius: 12px; padding: 12px 16px; margin-bottom: 10px;
    border-left: 3px solid; position: relative;
}
.flag-CRITICAL { background: rgba(248,113,113,0.07); border-color: #ef4444; }
.flag-HIGH     { background: rgba(251,146,60,0.07);  border-color: #f97316; }
.flag-MEDIUM   { background: rgba(251,191,36,0.07);  border-color: #f59e0b; }
.flag-LOW      { background: rgba(74,222,128,0.07);  border-color: #22c55e; }
.flag-title { font-size: 0.88rem; font-weight: 600; color: #d0dae8; margin: 0 0 5px; display: flex; align-items: center; gap: 8px; }
.flag-detail { font-size: 0.8rem; color: #6b7a93; line-height: 1.6; margin: 0; }
.flag-badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em; }
.badge-CRITICAL { background: rgba(239,68,68,0.2);   color: #f87171; }
.badge-HIGH     { background: rgba(249,115,22,0.2);  color: #fb923c; }
.badge-MEDIUM   { background: rgba(245,158,11,0.2);  color: #fbbf24; }
.badge-LOW      { background: rgba(34,197,94,0.2);   color: #4ade80; }

/* ── Safe clause chips ── */
.safe-chip { display: inline-flex; align-items: center; gap: 5px; background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2); border-radius: 99px;
    padding: 4px 12px; font-size: 0.78rem; color: #4ade80; margin: 3px 3px 3px 0; }

/* ── Translation block ── */
.lang-block { margin-bottom: 1rem; }
.lang-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #4a5568; margin-bottom: 6px; }
.lang-text { font-size: 1.05rem; color: #c8d6e8; line-height: 1.9; background: #07090f; border: 1px solid #1e2736; border-radius: 10px; padding: 10px 14px; }

/* ── Negotiation tip ── */
.tip-item { display: flex; gap: 12px; margin-bottom: 12px; align-items: flex-start; }
.tip-num { width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg,#1d4ed8,#3b82f6); color: white; font-size: 0.75rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; }
.tip-text { font-size: 0.88rem; color: #8899aa; line-height: 1.7; }

/* ── Footer ── */
.footer { text-align: center; padding: 2rem 0 1rem; color: #2e3a4a; font-size: 0.78rem; border-top: 1px solid #0d1117; margin-top: 2rem; }
.footer a { color: #3b82f6; text-decoration: none; }

/* ── No-result placeholder ── */
.placeholder {
    text-align: center; padding: 4rem 2rem;
    background: #0d1117; border: 1px dashed #1e2736;
    border-radius: 20px; margin-top: 1.5rem;
}
.placeholder-icon { font-size: 3rem; margin-bottom: 1rem; }
.placeholder-title { font-size: 1.1rem; font-weight: 600; color: #4a5568; margin-bottom: 0.5rem; }
.placeholder-sub { font-size: 0.85rem; color: #2e3a4a; }

/* ── selectbox & slider theming ── */
[data-testid="stSelectbox"] > div { border-radius: 10px !important; background: #0f1923 !important; border-color: #1e2736 !important; }
div[data-baseweb="select"] > div { background: #0f1923 !important; border-color: #1e2736 !important; border-radius: 10px !important; color: #d0dae8 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🛡️</div>
        <div>
            <div class="sidebar-logo-text">ContractGuard</div>
            <div class="sidebar-logo-sub">Legal BS Detector · v2.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stat-pill"><div class="stat-pill-dot" style="background:#3b82f6"></div><div class="stat-pill-text">⚡ Powered by Groq LPU inference</div></div>
    <div class="stat-pill"><div class="stat-pill-dot" style="background:#4ade80"></div><div class="stat-pill-text">🔒 Encrypted in transit · HTTPS</div></div>
    <div class="stat-pill"><div class="stat-pill-dot" style="background:#a78bfa"></div><div class="stat-pill-text">🌐 Hindi & Gujarati translations</div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">AI Model</div>', unsafe_allow_html=True)
    available = get_available_models()
    selected_model = st.selectbox(
        "Model", options=available, format_func=get_model_label,
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section">Analysis Temperature</div>', unsafe_allow_html=True)
    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=0.5, value=0.1, step=0.05,
        help="Lower = more consistent JSON. Keep at 0.1 for best results.",
        label_visibility="collapsed",
    )
    st.caption(f"Current: `{temperature}` · {'Precise ✓' if temperature <= 0.15 else 'Creative'}")

    st.markdown("---")

    # API key — secrets first, then manual input
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

    if _secret_key:
        api_key = _secret_key
        st.markdown("""
        <div class="stat-pill">
            <div class="stat-pill-dot" style="background:#4ade80"></div>
            <div class="stat-pill-text">API key configured ✓</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-section">Groq API Key</div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "Groq API Key", type="password", placeholder="gsk_...",
            label_visibility="collapsed",
        )
        st.caption("[Get a free key at console.groq.com →](https://console.groq.com)")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:#2e3a4a; line-height:1.8">
        Built with Python · Streamlit · LangChain · Groq<br>
        © 2026 ContractGuard · Educational use only
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge"><div class="hero-badge-dot"></div>AI-POWERED LEGAL ANALYSIS</div>
    <h1>Contract<span>Guard</span></h1>
    <p class="hero-sub">
        Paste any contract clause, lease, or terms of service and get an instant plain-English breakdown.<br>
        Red flags detected · Hindi & Gujarati translations · Negotiation tips — in under 10 seconds.
    </p>
    <div class="hero-stats">
        <div class="hero-stat"><div class="hero-stat-val">10+</div><div class="hero-stat-label">Red flag categories</div></div>
        <div class="hero-stat"><div class="hero-stat-val">3</div><div class="hero-stat-label">Languages supported</div></div>
        <div class="hero-stat"><div class="hero-stat-val">&lt;10s</div><div class="hero-stat-label">Analysis time</div></div>
        <div class="hero-stat"><div class="hero-stat-val">100%</div><div class="hero-stat-label">Free to use</div></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INPUT AREA
# ─────────────────────────────────────────────────────────────────────────────
contract_text = ""
tab_paste, tab_upload, tab_sample = st.tabs(["✍️  Paste Text", "📄  Upload File", "🧪  Try a Sample"])

with tab_paste:
    st.markdown("<br>", unsafe_allow_html=True)
    pasted = st.text_area(
        "Paste legal text",
        height=220,
        placeholder="Paste any contract clause, lease excerpt, or terms of service here...\n\ne.g. 'The Company reserves the right to amend these Terms at any time without prior notice...'",
        label_visibility="collapsed",
    )
    contract_text = pasted

with tab_upload:
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Upload Contract File")
    uploaded = st.file_uploader(
        "Choose a contract file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
    )
    st.caption("Use this uploader to extract contract text for analysis.")

    uploaded_img = None
    with st.expander("Optional: Upload Document Image for AI Type Classification"):
        uploaded_img = st.file_uploader(
            "Choose an image file (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            help="Upload a photo/scan of your contract to classify its type using the Teachable Machine model.",
            key="image_classifier_uploader",
        )

    # ── Phase 2: Teachable Machine document type classifier ──────────────────
    if uploaded_img is not None:
        img_bytes = uploaded_img.read()
        st.markdown('<div style="background:#0f1923;border:1px solid #1e3a5f;border-radius:14px;padding:1rem 1.2rem;margin-bottom:1rem">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
            <span style="font-size:1.1rem">🤖</span>
            <span style="font-size:0.85rem;font-weight:600;color:#60a5fa;letter-spacing:0.05em">PHASE 2 · TEACHABLE MACHINE CLASSIFIER</span>
        </div>""", unsafe_allow_html=True)

        with st.spinner("Classifying document type…"):
            result_cls = classify_document(img_bytes)

        if result_cls.get("model_available"):
            pred = result_cls["predicted_class"]
            conf = result_cls["confidence"]
            conf_color = "#4ade80" if conf >= 70 else ("#fbbf24" if conf >= 40 else "#f87171")
            st.markdown(f"""
            <div style="display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap">
                <div>
                    <div style="font-size:0.7rem;color:#4a5568;font-weight:600;letter-spacing:0.08em;margin-bottom:4px">DOCUMENT TYPE</div>
                    <div style="font-size:1.1rem;font-weight:700;color:#f0f6ff">{pred}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:#4a5568;font-weight:600;letter-spacing:0.08em;margin-bottom:4px">CONFIDENCE</div>
                    <div style="font-size:1.1rem;font-weight:700;color:{conf_color}">{conf}%</div>
                </div>
            </div>""", unsafe_allow_html=True)
            if result_cls.get("all_predictions"):
                st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
                for p in result_cls["all_predictions"][:4]:
                    bar_w = int(p["confidence"])
                    st.markdown(f"""
                    <div style="margin-bottom:4px">
                        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6b7a93;margin-bottom:2px">
                            <span>{p["label"]}</span><span>{p["confidence"]}%</span>
                        </div>
                        <div style="background:#1e2736;border-radius:99px;height:4px">
                            <div style="background:#3b82f6;width:{bar_w}%;height:4px;border-radius:99px"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-size:0.82rem;color:#fbbf24">
                ⚠️ Model not found. Place <code>keras_model.h5</code> and <code>labels.txt</code>
                in a <code>model/</code> folder. Train at
                <a href="https://teachablemachine.withgoogle.com" style="color:#60a5fa">teachablemachine.withgoogle.com</a>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if uploaded:
        with st.spinner("Extracting text…"):
            extracted = extract_text(uploaded)
        col_a, col_b = st.columns([3,1])
        with col_a:
            st.success(f"Extracted **{len(extracted):,}** characters from **{uploaded.name}**")
        with col_b:
            st.caption(f"{len(extracted.split()):,} words")
        st.text_area("Preview", extracted[:1200] + ("…" if len(extracted) > 1200 else ""), height=160, disabled=True, label_visibility="collapsed")
        contract_text = extracted

with tab_sample:
    st.markdown("<br>", unsafe_allow_html=True)
    SAMPLE = """TERMS OF SERVICE — SECTION 12: CHANGES TO TERMS
The Company reserves the right to modify or replace these Terms at any time at our sole discretion. We may provide notice of changes by updating the "Last Updated" date on this page. Your continued use of the Service after any changes constitutes your acceptance of the new Terms. You waive any right to specific notice of such changes.

SECTION 14: LIMITATION OF LIABILITY
To the maximum extent permitted by law, the Company shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits, data, or goodwill, even if the Company has been advised of the possibility of such damages. Your sole remedy for dissatisfaction with the Service is to stop using it.

SECTION 17: AUTO-RENEWAL
Your subscription will automatically renew at the then-current rate unless cancelled at least 30 days prior to the renewal date. Cancellation requests submitted less than 30 days before renewal will take effect in the following billing cycle. No refunds shall be issued for the current billing period under any circumstances.

SECTION 21: ARBITRATION & CLASS ACTION WAIVER
ALL DISPUTES SHALL BE RESOLVED BY BINDING ARBITRATION. YOU WAIVE YOUR RIGHT TO PARTICIPATE IN ANY CLASS ACTION LAWSUIT OR CLASS-WIDE ARBITRATION. The arbitration shall be conducted in Delaware, USA, and governed by Delaware law."""

    st.markdown("""
    <div style="background:#0f1923;border:1px solid #1e2736;border-radius:12px;padding:14px 18px;margin-bottom:14px;">
        <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.1em;color:#4a5568;margin-bottom:8px">SAMPLE PREVIEW</div>
        <div style="font-size:0.82rem;color:#6b7a93;line-height:1.7;font-family:monospace">""" + SAMPLE[:280] + """<span style="color:#3b82f6">…</span></div>
    </div>""", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([2, 3])
    with col_s1:
        if st.button("Load Sample Contract →", type="primary", use_container_width=True):
            st.session_state.sample_text = SAMPLE
            st.session_state.sample_loaded = True
            st.rerun()
    with col_s2:
        if st.session_state.sample_loaded:
            st.success("✅ Loaded — click **Scan Contract** below")


# ─────────────────────────────────────────────────────────────────────────────
# SCAN BUTTON
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
col_btn, col_meta = st.columns([2, 5])
with col_btn:
    scan_clicked = st.button("🔍 Scan Contract", type="primary", use_container_width=True)
with col_meta:
    st.markdown(f"""
    <div style="padding-top:10px;font-size:0.82rem;color:#4a5568">
        Model: <span style="color:#6b7a93">{selected_model}</span> &nbsp;·&nbsp;
        Temp: <span style="color:#6b7a93">{temperature}</span> &nbsp;·&nbsp;
        <span style="color:#3b82f6">⚡ Groq cloud inference</span>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS + RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if scan_clicked:
    active_text = (st.session_state.sample_text if st.session_state.sample_loaded else contract_text).strip()

    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar. Get one free at console.groq.com")
        st.stop()
    if not active_text:
        st.warning("⚠️ Please paste some text, upload a file, or load the sample first.")
        st.stop()
    if len(active_text) < 50:
        st.warning("⚠️ Text is too short. Please paste a full clause or paragraph.")
        st.stop()

    with st.spinner("ContractGuard is reading the fine print…"):
        start = time.time()
        try:
            result = analyse_contract(active_text, model_name=selected_model, api_key=api_key)
            st.session_state.result = result
            st.session_state.elapsed = round(time.time() - start, 1)
        except Exception as e:
            st.error(f"**Analysis failed:** {e}")
            st.info("Check your Groq API key and internet connection.")
            st.stop()

# Render results from session_state so they survive reruns
result = st.session_state.result
elapsed = st.session_state.elapsed

if result:
    verdict_raw = result.get("overall_verdict", "NEGOTIATE")
    verdict_key = verdict_raw.replace(" ", "").upper()
    risk        = result.get("risk_level", "MEDIUM")
    red_flags   = result.get("red_flags", [])
    safe        = result.get("safe_clauses", [])
    tips        = result.get("negotiation_tips", [])

    verdict_icons = {"SIGN": "✅", "NEGOTIATE": "⚠️", "DONOTSIGN": "🚫"}
    v_icon = verdict_icons.get(verdict_key, "⚠️")
    css_v  = "verdict-SIGN" if verdict_key == "SIGN" else ("verdict-DONOT" if "DONOT" in verdict_key else "verdict-NEGOTIATE")

    # ── Metric bar ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-card-label">Verdict</div>
            <div class="metric-card-val" style="font-size:1.1rem">{v_icon} {verdict_raw}</div>
        </div>
        <div class="metric-card">
            <div class="metric-card-label">Risk Level</div>
            <div class="metric-card-val risk-{risk}">{risk}</div>
        </div>
        <div class="metric-card">
            <div class="metric-card-label">Red Flags</div>
            <div class="metric-card-val" style="color:{'#f87171' if len(red_flags)>0 else '#4ade80'}">{len(red_flags)}</div>
            <div class="metric-card-sub">{'found' if red_flags else 'clean'}</div>
        </div>
        <div class="metric-card">
            <div class="metric-card-label">Scan Time</div>
            <div class="metric-card-val" style="font-size:1.2rem">{elapsed}s</div>
            <div class="metric-card-sub">via Groq</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Verdict banner ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="verdict-wrap {css_v}">
        <div class="verdict-icon">{v_icon}</div>
        <div>
            <div class="verdict-label">Recommendation</div>
            <div class="verdict-text">{verdict_raw}</div>
            <div class="verdict-reason">{result.get("verdict_reason", "")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Three-column dashboard ────────────────────────────────────────────────
    col_l, col_m, col_r = st.columns(3, gap="medium")

    # LEFT — ELI5 + Translations
    with col_l:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title">
            <span class="section-title-icon">💡</span>
            <span class="section-title-text">Plain English Summary</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.92rem;color:#8899aa;line-height:1.8;margin:0 0 1rem">{result.get("eli5_summary","")}</p>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        st.markdown("""
        <div class="lang-label" style="display:flex;align-items:center;gap:6px">
            <span>🇮🇳</span> Hindi Translation
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="lang-text">{result.get("hindi_translation","")}</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lang-label" style="display:flex;align-items:center;gap:6px">
            <span>🏛️</span> Gujarati Translation
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="lang-text">{result.get("gujarati_translation","")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # MIDDLE — Red Flags
    with col_m:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        flag_count = len(red_flags)
        flag_color = "#f87171" if flag_count >= 3 else ("#fbbf24" if flag_count > 0 else "#4ade80")
        st.markdown(f"""
        <div class="section-title">
            <span class="section-title-icon">{'🚨' if flag_count else '🟢'}</span>
            <span class="section-title-text">Red Flags &nbsp;<span style="color:{flag_color};font-weight:700">{flag_count}</span></span>
        </div>""", unsafe_allow_html=True)

        if flag_count == 0:
            st.markdown("""
            <div style="text-align:center;padding:2rem 1rem">
                <div style="font-size:2.5rem;margin-bottom:0.5rem">✅</div>
                <div style="font-size:0.9rem;color:#4ade80;font-weight:600">No red flags detected</div>
                <div style="font-size:0.8rem;color:#2e3a4a;margin-top:4px">This clause appears fair and standard</div>
            </div>""", unsafe_allow_html=True)
        else:
            sev_order = {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3}
            for flag in sorted(red_flags, key=lambda f: sev_order.get(f.get("severity","LOW"),3)):
                sev = flag.get("severity","MEDIUM")
                st.markdown(f"""
                <div class="flag-item flag-{sev}">
                    <div class="flag-title">
                        {flag.get("title","Flag")}
                        <span class="flag-badge badge-{sev}">{sev}</span>
                    </div>
                    <p class="flag-detail">{flag.get("detail","")}</p>
                </div>""", unsafe_allow_html=True)

        if safe:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown('<div class="lang-label">Fair clauses</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="safe-chip">✓ {s}</span>' for s in safe)
            st.markdown(f'<div style="line-height:2.2">{chips}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT — Negotiation tips + JSON
    with col_r:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-title">
            <span class="section-title-icon">🎯</span>
            <span class="section-title-text">Negotiation Tips</span>
        </div>""", unsafe_allow_html=True)

        if tips:
            for i, tip in enumerate(tips, 1):
                st.markdown(f"""
                <div class="tip-item">
                    <div class="tip-num">{i}</div>
                    <div class="tip-text">{tip}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-size:0.85rem;color:#4a5568">No specific negotiation points identified for this clause.</p>', unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        with st.expander("📋 View raw JSON output"):
            st.json(result)

        st.markdown("""
        <div style="margin-top:1rem;background:#07090f;border:1px solid #1e2736;border-radius:10px;padding:10px 14px;font-size:0.75rem;color:#2e3a4a;display:flex;align-items:center;gap:8px">
            <span>⚡</span> Analysed via Groq cloud · TLS encrypted · not stored
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Placeholder (no result yet) ───────────────────────────────────────────────
elif not scan_clicked:
    st.markdown("""
    <div class="placeholder">
        <div class="placeholder-icon">🛡️</div>
        <div class="placeholder-title">Ready to analyse your contract</div>
        <div class="placeholder-sub">Paste text or upload a file above, then click <strong>Scan Contract</strong></div>
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    ⚠️ ContractGuard is an AI tool for <strong>educational purposes only</strong>.
    It is not a substitute for qualified legal advice.
    Always consult a licensed lawyer before signing important contracts.<br><br>
    Built by <a href="#">Dev Solanki</a> · Powered by <a href="https://groq.com">Groq</a> + <a href="https://streamlit.io">Streamlit</a>
</div>""", unsafe_allow_html=True)
