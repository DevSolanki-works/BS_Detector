# app.py
# ─────────────────────────────────────────────────────────────────────────────
# ContractGuard: The Local Legal BS Detector
# Run with: streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import time
import json

from src.llm_handler import analyse_contract, get_available_models, get_model_label
from src.doc_parser import extract_text


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ContractGuard · Legal BS Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global resets ── */
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }

/* ── Typography ── */
h1 { font-size: 2rem !important; font-weight: 700 !important; }
h2 { font-size: 1.25rem !important; font-weight: 600 !important; }
.sub { color: #8b949e; font-size: 0.9rem; margin-top: -8px; margin-bottom: 20px; }

/* ── Risk badge colours ── */
.badge { display: inline-block; padding: 4px 14px; border-radius: 99px;
         font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; }
.badge-LOW      { background: #0d4429; color: #3fb950; border: 1px solid #238636; }
.badge-MEDIUM   { background: #2d2a0e; color: #d29922; border: 1px solid #9e6a03; }
.badge-HIGH     { background: #3d1f00; color: #f0883e; border: 1px solid #bd561d; }
.badge-CRITICAL { background: #490202; color: #ff7b72; border: 1px solid #da3633; }

/* ── Verdict banner colours ── */
.verdict-SIGN      { background:#0d3321; border:1px solid #238636; border-radius:10px;
                     padding:16px 20px; color:#3fb950; }
.verdict-NEGOTIATE { background:#2d2a0e; border:1px solid #9e6a03; border-radius:10px;
                     padding:16px 20px; color:#d29922; }
.verdict-DONOT     { background:#490202; border:1px solid #da3633; border-radius:10px;
                     padding:16px 20px; color:#ff7b72; }

/* ── Flag cards ── */
.flag-card { background:#161b22; border:1px solid #30363d; border-radius:10px;
             padding:14px 18px; margin-bottom:10px; }
.flag-card h4 { margin:0 0 4px 0; font-size:0.95rem; }
.flag-card p  { margin:0; font-size:0.85rem; color:#8b949e; }

/* ── Section cards ── */
.card { background:#161b22; border:1px solid #30363d; border-radius:12px;
        padding:20px 22px; margin-bottom:14px; }
.card h2 { margin-bottom: 12px; }

/* ── Privacy pill ── */
.privacy-pill { background:#0d1117; border:1px solid #30363d; border-radius:99px;
                padding:6px 14px; font-size:0.78rem; color:#8b949e;
                display:inline-flex; align-items:center; gap:6px; }

/* ── Safe clause list ── */
.safe-item { color:#3fb950; font-size:0.9rem; padding: 3px 0; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ ContractGuard")
    st.markdown('<p class="sub">Local Legal BS Detector</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Privacy badge
    st.markdown("""
    <div class="privacy-pill">🔒 100% Local · Zero data sent to cloud</div>
    """, unsafe_allow_html=True)
    st.markdown(" ")

    # Model picker
    st.markdown("#### AI Model")
    available = get_available_models()
    selected_model = st.selectbox(
        "Select local model",
        options=available,
        format_func=get_model_label,
        label_visibility="collapsed",
    )

    st.markdown("#### Analysis depth")
    temperature = st.slider(
        "Creativity (lower = more consistent)",
        min_value=0.0, max_value=0.5, value=0.1, step=0.05,
        help="Keep this low (0.1) for consistent JSON output."
    )

    st.markdown("---")
    # ── API key: read from Streamlit Cloud secrets first, manual input as fallback ──
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

    if _secret_key:
        api_key = _secret_key
        st.success("API key loaded automatically", icon="🔑")
    else:
        st.markdown("#### Groq API key")
        api_key = st.text_input(
            "Enter your free Groq API key",
            type="password",
            placeholder="gsk_...",
            help="Get a free key at console.groq.com",
            label_visibility="collapsed",
        )
        st.caption("[Get a free key → console.groq.com](https://console.groq.com)")

    st.markdown("---")
    st.caption("Built with 🐍 Python · Streamlit · LangChain · Groq")
    st.caption("⚡ ~3 second responses · Free tier · No install needed")


# ── Main area header ──────────────────────────────────────────────────────────
st.markdown("# 🛡️ ContractGuard")
st.markdown('<p class="sub">Paste or upload a contract · Get instant red-flag analysis · 100% local & private</p>', unsafe_allow_html=True)

tab_paste, tab_upload, tab_sample = st.tabs(["📋 Paste Text", "📄 Upload File", "🧪 Try a Sample"])


# ── Input helpers ──────────────────────────────────────────────────────────────
contract_text = ""

with tab_paste:
    pasted = st.text_area(
        "Paste your legal clause or full contract here",
        height=260,
        placeholder=(
            "e.g. 'The Company reserves the right to amend these Terms at any time "
            "without prior notice. Continued use of the Service constitutes acceptance "
            "of the revised Terms...'"
        ),
    )
    contract_text = pasted

with tab_upload:
    uploaded = st.file_uploader(
        "Upload a contract (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
    )
    if uploaded:
        with st.spinner("Extracting text from file..."):
            extracted = extract_text(uploaded)
        st.success(f"✅ Extracted {len(extracted):,} characters from **{uploaded.name}**")
        st.text_area("Extracted text (read-only)", extracted, height=200, disabled=True)
        contract_text = extracted

with tab_sample:
    SAMPLE = """TERMS OF SERVICE — SECTION 12: CHANGES TO TERMS
The Company reserves the right to modify or replace these Terms at any time at our sole
discretion. We may provide notice of changes by updating the "Last Updated" date on this
page. Your continued use of the Service after any changes constitutes your acceptance of
the new Terms. You waive any right to specific notice of such changes.

SECTION 14: LIMITATION OF LIABILITY
To the maximum extent permitted by law, the Company shall not be liable for any indirect,
incidental, special, consequential, or punitive damages, including loss of profits, data,
or goodwill, even if the Company has been advised of the possibility of such damages.
Your sole remedy for dissatisfaction with the Service is to stop using it.

SECTION 17: AUTO-RENEWAL
Your subscription will automatically renew at the then-current rate unless cancelled at
least 30 days prior to the renewal date. Cancellation requests submitted less than 30 days
before renewal will take effect in the following billing cycle. No refunds shall be issued
for the current billing period under any circumstances.

SECTION 21: ARBITRATION & CLASS ACTION WAIVER
ALL DISPUTES SHALL BE RESOLVED BY BINDING ARBITRATION. YOU WAIVE YOUR RIGHT TO PARTICIPATE
IN ANY CLASS ACTION LAWSUIT OR CLASS-WIDE ARBITRATION. The arbitration shall be conducted
in Delaware, USA, and governed by Delaware law."""

    st.code(SAMPLE[:300] + "...", language="text")
    if st.button("Load this sample"):
        contract_text = SAMPLE
        st.success("Sample loaded — click 'Scan for BS' below!")


# ── Scan button ───────────────────────────────────────────────────────────────
st.markdown("---")
col_btn, col_info = st.columns([2, 5])
with col_btn:
    scan_clicked = st.button("🔍 Scan for BS", type="primary", use_container_width=True)
with col_info:
    st.markdown(" ")
    st.caption(f"Using **{selected_model}** · All processing happens locally on your machine.")


# ── Analysis & Results ────────────────────────────────────────────────────────
if scan_clicked:
    active_text = contract_text.strip()

    if not api_key:
        st.warning("Please enter your Groq API key in the sidebar first. Get one free at console.groq.com")
        st.stop()

    if not active_text:
        st.warning("Please paste some text, upload a file, or load the sample first.")
        st.stop()

    if len(active_text) < 50:
        st.warning("The text is too short. Please paste a full clause or section.")
        st.stop()

    # ── Run analysis ──────────────────────────────────────────────────────────
    with st.spinner(f"ContractGuard is analysing with {selected_model} via Groq — usually takes 3–10s…"):
        start = time.time()
        try:
            result = analyse_contract(active_text, model_name=selected_model, api_key=api_key)
            elapsed = time.time() - start
        except Exception as e:
            st.error(f"**Analysis failed:** {e}")
            st.info("Check your Groq API key is correct and you have internet access.")
            st.stop()

    st.success(f"✅ Analysis complete in {elapsed:.1f}s")
    st.markdown("---")

    # ── Top row: verdict + risk level ─────────────────────────────────────────
    verdict_raw = result.get("overall_verdict", "NEGOTIATE")
    verdict_key = verdict_raw.replace(" ", "").upper()
    risk = result.get("risk_level", "MEDIUM")

    verdict_icons = {"SIGN": "✅", "NEGOTIATE": "⚠️", "DONOTSIGN": "🚫"}
    icon = verdict_icons.get(verdict_key, "⚠️")

    col_v, col_r = st.columns([3, 1])
    with col_v:
        css_class = "verdict-SIGN" if verdict_key == "SIGN" else ("verdict-DONOT" if "DONOT" in verdict_key else "verdict-NEGOTIATE")
        st.markdown(f"""
        <div class="{css_class}">
          <strong style="font-size:1.2rem">{icon} Verdict: {verdict_raw}</strong><br>
          <span style="font-size:0.9rem">{result.get("verdict_reason", "")}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown(f"""
        <div style="text-align:center; padding-top:10px;">
          <div style="font-size:0.75rem; color:#8b949e; margin-bottom:6px;">RISK LEVEL</div>
          <span class="badge badge-{risk}">{risk}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(" ")

    # ── Three-column dashboard ────────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([2, 2, 2])

    # ── LEFT: ELI5 Summary ────────────────────────────────────────────────────
    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 💡 ELI5 Summary")
        st.markdown(result.get("eli5_summary", "No summary generated."))

        st.markdown("---")
        st.markdown("#### 🇮🇳 Hindi")
        st.markdown(f'<p style="font-size:1.05rem; line-height:1.8">{result.get("hindi_translation", "")}</p>', unsafe_allow_html=True)

        st.markdown("#### 🏛️ Gujarati")
        st.markdown(f'<p style="font-size:1.05rem; line-height:1.8">{result.get("gujarati_translation", "")}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── MIDDLE: Red Flags ─────────────────────────────────────────────────────
    with col_mid:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        red_flags = result.get("red_flags", [])
        flag_count = len(red_flags)

        if flag_count == 0:
            st.markdown("## 🟢 Red Flags (0)")
            st.success("No major red flags detected. This clause appears standard.")
        else:
            st.markdown(f"## 🚨 Red Flags ({flag_count})")
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            for flag in sorted(red_flags, key=lambda f: severity_order.get(f.get("severity", "LOW"), 3)):
                sev = flag.get("severity", "MEDIUM")
                st.markdown(f"""
                <div class="flag-card">
                  <h4>{flag.get("title", "Unnamed Flag")} 
                    <span class="badge badge-{sev}" style="font-size:0.7rem">{sev}</span>
                  </h4>
                  <p>{flag.get("detail", "")}</p>
                </div>
                """, unsafe_allow_html=True)

        # Safe clauses
        safe = result.get("safe_clauses", [])
        if safe:
            st.markdown("---")
            st.markdown("#### ✅ Fair Clauses")
            for s in safe:
                st.markdown(f'<div class="safe-item">· {s}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT: Action Steps ───────────────────────────────────────────────────
    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 🎯 Negotiation Tips")
        tips = result.get("negotiation_tips", [])
        if tips:
            for i, tip in enumerate(tips, 1):
                st.markdown(f"**{i}.** {tip}")
                st.markdown(" ")
        else:
            st.info("No specific negotiation points identified.")

        st.markdown("---")
        st.markdown("#### 📋 Raw JSON Output")
        with st.expander("View full analysis JSON"):
            st.json(result)

        st.markdown("---")
        st.markdown('<div class="privacy-pill">⚡ Analysed via Groq cloud · encrypted in transit</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⚠️ ContractGuard is an AI tool for educational purposes. It is not a substitute for qualified legal advice. Always consult a lawyer before signing important contracts.")
