import os
import time
import tempfile
import streamlit as st
from dotenv import load_dotenv
from pipeline import run_research_pipeline
from tools.pdf_export import export_to_pdf

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Dark background */
  .stApp {
    background: #0a0f1e;
    color: #e2e8f0;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0d1526;
    border-right: 1px solid #1e3a5f;
  }

  /* Main header */
  .hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
  }

  .hero-subtitle {
    color: #64748b;
    font-size: 1.05rem;
    font-weight: 300;
    margin-bottom: 2rem;
  }

  /* Agent step cards */
  .agent-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.3s ease;
  }

  .agent-card.active {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59,130,246,0.15);
  }

  .agent-card.done {
    border-color: #10b981;
    box-shadow: 0 0 12px rgba(16,185,129,0.1);
  }

  .agent-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: #f1f5f9;
  }

  .agent-desc {
    font-size: 0.82rem;
    color: #64748b;
    margin-top: 2px;
  }

  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;
  }

  .dot-idle    { background: #334155; }
  .dot-active  { background: #3b82f6; animation: pulse 1s infinite; }
  .dot-done    { background: #10b981; }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* Score badge */
  .score-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1e40af, #7c3aed);
    color: white;
    font-size: 1.6rem;
    font-weight: 700;
    padding: 0.4rem 1.1rem;
    border-radius: 50px;
    font-family: 'DM Serif Display', serif;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
  }

  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 500;
  }

  .stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #60a5fa !important;
  }

  /* Input */
  .stTextInput > div > div > input,
  .stTextArea textarea {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
  }

  .stTextInput > div > div > input:focus,
  .stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    transition: opacity 0.2s;
  }

  .stButton > button:hover {
    opacity: 0.9 !important;
  }

  /* Download button */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #065f46, #0f766e) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
  }

  /* Selectbox */
  .stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
  }

  /* Metrics */
  [data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem;
  }

  [data-testid="stMetricValue"] {
    color: #60a5fa !important;
    font-family: 'DM Serif Display', serif !important;
  }

  hr { border-color: #1e3a5f; }

  /* Report markdown */
  .report-container {
    background: #0d1526;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 2rem;
    line-height: 1.8;
  }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.divider()

    google_key = st.text_input(
        "Google API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Get yours at aistudio.google.com",
    )
    tavily_key = st.text_input(
        "Tavily API Key",
        type="password",
        value=os.getenv("TAVILY_API_KEY", ""),
        help="Get yours at tavily.com",
    )

    st.divider()
    depth = st.selectbox(
        "Research Depth",
        ["quick", "standard", "deep"],
        index=1,
        help="Quick: 3 sub-questions | Standard: 5 | Deep: 7",
    )

    depth_info = {
        "quick": ("~2 min", "3 sub-questions", "Best for simple topics"),
        "standard": ("~4 min", "5 sub-questions", "Balanced depth"),
        "deep": ("~7 min", "7 sub-questions", "Comprehensive coverage"),
    }
    info = depth_info[depth]
    st.caption(f"⏱ Est. time: {info[0]}  •  {info[1]}  •  {info[2]}")

    st.divider()

    # Agent pipeline visualization
    st.markdown("### 🤖 Agent Pipeline")

    agents_info = [
        ("🗺️", "Planner", "Breaks topic into sub-questions"),
        ("🔍", "Web Researcher", "Searches the web"),
        ("🎓", "Academic Researcher", "Searches ArXiv & PubMed"),
        ("📝", "Summarizer", "Distills key insights"),
        ("🧐", "Critic", "Reviews & scores quality"),
        ("✍️", "Writer", "Writes final report"),
    ]

    agent_status = st.session_state.get("agent_status", ["idle"] * 6)

    for i, (emoji, name, desc) in enumerate(agents_info):
        status = agent_status[i] if i < len(agent_status) else "idle"
        dot_class = f"dot-{status}"
        card_class = f"agent-card {status if status != 'idle' else ''}"
        st.markdown(f"""
        <div class="{card_class}">
          <span class="status-dot {dot_class}"></span>
          <span class="agent-name">{emoji} {name}</span>
          <div class="agent-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.caption("Powered by Google Gemini 2.0 Flash + CrewAI")


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Multi-agent research pipeline • Powered by Google Gemini 2.0 Flash</div>', unsafe_allow_html=True)

# Topic input
col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. The impact of large language models on software engineering jobs",
        label_visibility="collapsed",
    )
with col2:
    run_btn = st.button("🚀 Research", use_container_width=True)


# Example topics
st.caption("Try: &nbsp; `Quantum computing in 2025` &nbsp;•&nbsp; `AI regulation in Europe` &nbsp;•&nbsp; `CRISPR gene editing advances` &nbsp;•&nbsp; `Future of nuclear energy`")

st.divider()


# ── Run Pipeline ──────────────────────────────────────────────────────────────
def update_agent_status(index: int, status: str):
    """Update agent status in session state and rerun sidebar."""
    statuses = st.session_state.get("agent_status", ["idle"] * 5)
    statuses[index] = status
    st.session_state["agent_status"] = statuses


if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    elif not google_key:
        st.error("Please enter your Google API Key in the sidebar.")
    elif not tavily_key:
        st.error("Please enter your Tavily API Key in the sidebar.")
    else:
        # Inject keys into environment
        os.environ["GOOGLE_API_KEY"] = google_key
        os.environ["TAVILY_API_KEY"] = tavily_key

        # Reset agent statuses
        st.session_state["agent_status"] = ["idle"] * 6
        st.session_state["results"] = None

        # Progress UI
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        agent_names = ["Planner", "Researcher", "Summarizer", "Critic", "Writer"]

        # Simulate step-by-step status updates (we update before/after actual pipeline)
        try:
            status_text.markdown("**🗺️ Planner Agent** is analyzing your topic...")
            update_agent_status(0, "active")
            progress_bar.progress(5)

            # Run the full pipeline (blocking call)
            # We update status text as a proxy since CrewAI runs sequentially
            import threading

            results = {}
            error_holder = {}

            def pipeline_thread():
                try:
                    results["data"] = run_research_pipeline(topic, depth)
                except Exception as e:
                    error_holder["error"] = str(e)

            thread = threading.Thread(target=pipeline_thread)
            thread.start()

            step_messages = [
                (8,  0, "active", "**🗺️ Planner Agent** breaking topic into sub-questions..."),
                (18, 0, "done",   "**🔍 Web Researcher** searching the web..."),
                (18, 1, "active", "**🔍 Web Researcher** searching the web..."),
                (35, 1, "done",   "**🎓 Academic Researcher** searching ArXiv & PubMed..."),
                (35, 2, "active", "**🎓 Academic Researcher** searching ArXiv & PubMed..."),
                (55, 2, "done",   "**📝 Summarizer** distilling all findings..."),
                (55, 3, "active", "**📝 Summarizer** distilling all findings..."),
                (72, 3, "done",   "**🧐 Critic** reviewing and scoring..."),
                (72, 4, "active", "**🧐 Critic** reviewing and scoring..."),
                (88, 4, "done",   "**✍️ Writer** composing the final report..."),
                (88, 5, "active", "**✍️ Writer** composing the final report..."),
            ]

            step_idx = 0
            while thread.is_alive():
                if step_idx < len(step_messages):
                    prog, agent_i, agent_s, msg = step_messages[step_idx]
                    progress_bar.progress(prog)
                    status_text.markdown(msg)
                    update_agent_status(agent_i, agent_s)
                    step_idx += 1
                time.sleep(8)

            # Thread finished — wait to be safe then collect results
            thread.join(timeout=30)

            if "error" in error_holder:
                st.error(f"Pipeline error: {error_holder['error']}")
            elif "data" not in results:
                st.error("Pipeline completed but returned no data. Please try again.")
            else:
                # Mark all done
                st.session_state["agent_status"] = ["done"] * 6
                progress_bar.progress(100)
                status_text.markdown("✅ **Research complete!**")
                st.session_state["results"] = results["data"]
                st.session_state["topic"] = topic
                time.sleep(0.5)
                st.rerun()

        except Exception as e:
            import traceback
            st.error(f"An error occurred: {e}")
            st.code(traceback.format_exc())
            st.session_state["agent_status"] = ["idle"] * 6


# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.get("results"):
    results = st.session_state["results"]
    topic_display = st.session_state.get("topic", "Research")

    # Metrics row
    word_count = len(results["final_report"].split())
    source_count = results["final_report"].lower().count("http")

    # Extract critic score
    import re
    score_match = re.search(r'(\d+)\s*/\s*10', results.get("critique", ""))
    score = score_match.group(0) if score_match else "—"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📄 Report Words", f"{word_count:,}")
    m2.metric("🔗 Sources Found", max(source_count, 1))
    m3.metric("🧐 Critic Score", score)
    m4.metric("🤖 Agents Used", "5")

    st.divider()

    # Tabs for each agent output
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Final Report",
        "🗺️ Research Plan",
        "🔍 Web Research",
        "🎓 Academic Papers",
        "📝 Summary",
        "🧐 Critique",
    ])

    with tab1:
        st.markdown("### 📋 Final Research Report")
        col_report, col_dl = st.columns([5, 1])
        with col_dl:
            # Generate PDF for download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf_path = tmp.name
            export_to_pdf(topic_display, results["final_report"], pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF",
                    data=f.read(),
                    file_name=f"research_{topic_display[:30].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(results["final_report"])
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🗺️ Research Plan")
        st.caption("Sub-questions generated by the Planner Agent")
        st.markdown(results["plan"])

    with tab3:
        st.markdown("### 🔍 Web Research")
        st.caption("Web search results gathered by the Web Researcher Agent")
        with st.expander("View web research data", expanded=False):
            st.markdown(results["raw_research"])

    with tab4:
        st.markdown("### 🎓 Academic Papers")
        st.caption("Peer-reviewed papers from ArXiv & PubMed — no API key required")
        st.markdown(results.get("academic_research", "_No academic results found._"))

    with tab5:
        st.markdown("### 📝 Summarized Insights")
        st.caption("Key findings distilled by the Summarizer Agent")
        st.markdown(results["summary"])

    with tab6:
        st.markdown("### 🧐 Critic's Review")
        st.caption("Quality assessment and improvement notes from the Critic Agent")
        if score_match:
            st.markdown(f'<div style="margin-bottom:1rem"><span class="score-badge">Score: {score}</span></div>', unsafe_allow_html=True)
        st.markdown(results["critique"])