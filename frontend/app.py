import streamlit as st
import os
import sys
import base64
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TripMind AI - Intelligent Travel Planning",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State ───────────────────────────────────────────────────────────
if "chat_history"     not in st.session_state: st.session_state.chat_history     = []
if "pending_image"    not in st.session_state: st.session_state.pending_image    = None
if "pending_img_type" not in st.session_state: st.session_state.pending_img_type = None
if "pending_img_name" not in st.session_state: st.session_state.pending_img_name = None
if "trigger_prompt"   not in st.session_state: st.session_state.trigger_prompt   = None
if "uploader_key"     not in st.session_state: st.session_state.uploader_key     = 0

# ── SVG Icon Helper ─────────────────────────────────────────────────────────
def svg(name, size=18, color="currentColor"):
    s = str(size)
    paths = {
        "globe":     '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2c-2.667 3.333-4 6.667-4 10s1.333 6.667 4 10M12 2c2.667 3.333 4 6.667 4 10s-1.333 6.667-4 10"/>',
        "plane":     '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21 4 21 4s-2 0-3.5 1.5L14 9 5.8 6.2l-2.06 2.06 6.38 3.19L6.39 15l-1.95-.65L3 15.76l3.5 1.5L8 20.5l1.44-1.44L8.8 17.2l3.74-3.74 3.19 6.38 2.06-2.06z"/>',
        "map":       '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>',
        "paperclip": '<path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>',
        "compass":   '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    }
    p = paths.get(name, "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{p}</svg>')


# ═══════════════════════════════════════════════════════════════════════════
# STYLESHEET — lightweight, lets Streamlit config.toml handle base colors
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Typography ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Hide Streamlit Chrome ── */
[data-testid="stDecoration"], [data-testid="stToolbar"], footer {
    visibility: hidden !important; height: 0 !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Container ── */
.block-container {
    padding: 1rem 1.5rem !important;
    max-width: 840px !important;
    margin: 0 auto !important;
}

/* ═══ TOP BAR ═══ */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    background: rgba(26,29,46,0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin: -1rem -1.5rem 1.5rem -1.5rem;
    border-radius: 0 0 16px 16px;
    animation: topSlide 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
@keyframes topSlide {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.topbar-left { display: flex; align-items: center; gap: 0.6rem; }
.topbar-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #7c74ff, #6358e8);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 20px rgba(124,116,255,0.35);
}
.topbar-title {
    font-size: 16px; font-weight: 700;
    color: #fafafa; letter-spacing: -0.4px;
}
.topbar-label {
    font-size: 9.5px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #7c74ff;
    background: rgba(124,116,255,0.15);
    border: 1px solid rgba(124,116,255,0.2);
    border-radius: 5px; padding: 2px 6px;
}
.topbar-right {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 12px; color: #8890aa; font-weight: 500;
}

/* ═══ WELCOME HERO ═══ */
.welcome {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 5rem 1.5rem 2rem; text-align: center;
    animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
.welcome-icon {
    width: 76px; height: 76px;
    background: linear-gradient(135deg, #7c74ff, #6358e8);
    border-radius: 22px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 16px 48px rgba(124,116,255,0.3);
    animation: iconFloat 5s ease-in-out infinite;
}
@keyframes iconFloat {
    0%,100% { transform: translateY(0) rotate(0deg); }
    50%     { transform: translateY(-6px) rotate(1.5deg); }
}
.welcome h2 {
    font-size: 38px; font-weight: 900;
    color: #fafafa; letter-spacing: -1.5px;
    margin-bottom: 0.5rem;
}
.welcome p {
    font-size: 15px; color: #8890aa;
    max-width: 420px; line-height: 1.65;
    margin-bottom: 2rem;
}

/* ═══ SIDEBAR BRAND ═══ */
.sb-brand {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 1.25rem 1.25rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sb-brand-name { font-size: 15px; font-weight: 800; color: #fafafa !important; }
.sb-brand-sub { font-size: 10.5px; color: #8890aa !important; }
.sb-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #7c74ff, #6358e8);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 16px rgba(124,116,255,0.3);
}
.sb-section { padding: 1rem 1.25rem 0.25rem; }
.sb-label {
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #8890aa !important; margin-bottom: 0.5rem; display: block;
}
.sb-sep { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 0.75rem 0; }

/* ═══ STATUS PILLS ═══ */
.status-pill {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.45rem 0.7rem;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; font-size: 12.5px;
    color: #c8cde0 !important; margin-bottom: 0.3rem;
}
.sdot { width: 7px; height: 7px; border-radius: 50%; }
.sdot-green  { background: #22c997; animation: dotPulse 2.5s ease-in-out infinite; }
.sdot-red    { background: #f05e5e; }
.sdot-yellow { background: #f0a830; }
@keyframes dotPulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(34,201,151,0.4); }
    50%     { box-shadow: 0 0 0 4px transparent; }
}
.spill {
    margin-left: auto; font-size: 10.5px; font-weight: 600;
    padding: 2px 7px; border-radius: 99px;
}
.spill-ok   { color: #22c997; background: rgba(34,201,151,0.12); }
.spill-warn { color: #f0a830; background: rgba(240,168,48,0.12); }
.spill-err  { color: #f05e5e; background: rgba(240,94,94,0.12); }

/* ═══ CHAT MESSAGES ═══ */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.7rem !important;
    animation: msgSlide 0.4s cubic-bezier(0.16,1,0.3,1) both;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stChatMessage"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.2) !important;
}
@keyframes msgSlide {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    font-size: 14px !important;
    line-height: 1.75 !important;
}

/* Avatar styling */
[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, #7c74ff, #6358e8) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(124,116,255,0.3) !important;
}

/* ═══ CHAT INPUT ═══ */
[data-testid="stChatInput"] > div {
    border-radius: 14px !important;
    border: 1.5px solid rgba(255,255,255,0.08) !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(124,116,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(124,116,255,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #7c74ff, #6358e8) !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(124,116,255,0.3) !important;
}

/* ═══ SIDEBAR BUTTONS ═══ */
section[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
    margin-bottom: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #7c74ff !important;
    color: white !important;
    border-color: #7c74ff !important;
    box-shadow: 0 6px 20px rgba(124,116,255,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ═══ MAIN AREA BUTTONS (chips) ═══ */
.block-container .stButton > button {
    border-radius: 99px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.35rem !important;
    transition: all 0.35s cubic-bezier(0.16,1,0.3,1) !important;
    letter-spacing: -0.2px !important;
}
.block-container .stButton > button:hover {
    background: #7c74ff !important;
    border-color: #7c74ff !important;
    color: #ffffff !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 10px 28px rgba(124,116,255,0.35) !important;
}

/* ═══ TYPING DOTS ═══ */
.typing-dots { display: flex; align-items: center; gap: 6px; padding: 6px 0; }
.typing-dots span {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; background: #7c74ff;
    animation: bounce 1.4s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.16s; }
.typing-dots span:nth-child(3) { animation-delay: 0.32s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
    40%           { transform: scale(1.2); opacity: 1; }
}

/* ═══ FILE UPLOADER ═══ */
[data-testid="stFileUploaderDropzone"] {
    border-radius: 12px !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(124,116,255,0.5) !important;
}
[data-testid="stFileUploaderFileList"] { display: none !important; }

/* ═══ ATTACH AREA ═══ */
.attach-label {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 12px; color: #8890aa;
    padding: 0.2rem 0 0.3rem; font-weight: 500;
}
.thumb-strip {
    display: flex; align-items: center; gap: 0.5rem;
    background: rgba(124,116,255,0.08);
    border: 1px solid rgba(124,116,255,0.15);
    border-radius: 10px; padding: 0.4rem 0.7rem;
    font-size: 12px; color: #c8cde0;
    font-weight: 500; margin-bottom: 0.4rem; width: fit-content;
}
.thumb-strip img { width: 28px; height: 28px; border-radius: 6px; object-fit: cover; }
.attached-preview img {
    border-radius: 12px; max-width: 300px;
    margin-top: 0.5rem; display: block;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

/* ═══ ALERTS ═══ */
.stAlert { border-radius: 10px !important; }

/* ═══ RESPONSIVE ═══ */
@media (max-width: 768px) {
    .welcome h2 { font-size: 28px; }
    .welcome { padding: 3.5rem 1rem 1.5rem; }
    .welcome-icon { width: 60px; height: 60px; }
    .topbar-right { display: none; }
    .block-container {
        padding: 0.75rem 0.75rem !important;
        max-width: 100% !important;
    }
}
@media (max-width: 480px) {
    .welcome h2 { font-size: 24px; }
    .welcome p { font-size: 14px; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-icon">{svg('compass', 19, '#ffffff')}</div>
        <div>
            <div class="sb-brand-name">TripMind AI</div>
            <div class="sb-brand-sub">Powered by Gemini</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="sb-sep">', unsafe_allow_html=True)

    # System Status
    st.markdown('<div class="sb-section"><span class="sb-label">System Status</span></div>', unsafe_allow_html=True)

    google_api_key    = os.getenv("GOOGLE_API_KEY")
    langsmith_api_key = os.getenv("LANGCHAIN_API_KEY")
    tavily_api_key    = os.getenv("TAVILY_API_KEY")

    gemini_ok  = bool(google_api_key    and google_api_key    != "your_google_api_key_here")
    tracing_ok = bool(langsmith_api_key and langsmith_api_key != "your_langsmith_api_key_here")
    search_ok  = bool(tavily_api_key    and tavily_api_key    != "your_tavily_api_key_here")

    def status_pill(label, ok, warn=False):
        dot   = "sdot-green" if ok else ("sdot-yellow" if warn else "sdot-red")
        badge = "spill-ok"   if ok else ("spill-warn"  if warn else "spill-err")
        state = "Active"     if ok else ("Optional"    if warn else "Missing")
        return (f'<div class="status-pill"><span class="sdot {dot}"></span>'
                f'<span>{label}</span>'
                f'<span class="spill {badge}">{state}</span></div>')

    st.markdown(
        '<div style="padding:0 1.25rem;">' +
        status_pill("Gemini AI", gemini_ok) +
        status_pill("LangSmith", tracing_ok, warn=not tracing_ok) +
        status_pill("Web Search", search_ok) +
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<hr class="sb-sep">', unsafe_allow_html=True)

    # Knowledge Base
    st.markdown('<div class="sb-section"><span class="sb-label">Knowledge Base</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:12px;color:#8890aa;padding:0 1.25rem 0.5rem;line-height:1.5;">'
        'Upload PDF or TXT travel documents for the AI to reference.</p>',
        unsafe_allow_html=True
    )

    uploaded_doc = st.file_uploader(
        "Upload document",
        type=["pdf", "txt"],
        label_visibility="collapsed",
        key="doc_uploader"
    )

    if uploaded_doc is not None:
        if not os.path.exists("data"):
            os.makedirs("data")
        dest = os.path.join("data", uploaded_doc.name)
        if os.path.exists(dest):
            st.info(f"Already indexed: **{uploaded_doc.name}**")
        else:
            try:
                with open(dest, "wb") as fh:
                    fh.write(uploaded_doc.getbuffer())
                st.success(f"Saved: **{uploaded_doc.name}**")
            except PermissionError:
                st.error(f"Cannot save -- close **{uploaded_doc.name}** first.")

    st.markdown('<div style="padding:0 1.25rem 0.5rem;">', unsafe_allow_html=True)
    from backend.rag import ingest_documents
    if st.button("Build Knowledge Base", use_container_width=True, key="btn_build"):
        with st.spinner("Indexing documents..."):
            if ingest_documents():
                st.success("Knowledge base ready.")
            else:
                st.warning("No documents found. Upload a file first.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-sep">', unsafe_allow_html=True)

    # Session
    st.markdown('<div class="sb-section"><span class="sb-label">Session</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 1.25rem 1rem;">', unsafe_allow_html=True)
    if st.button("Clear Conversation", use_container_width=True, key="btn_clear"):
        st.session_state.chat_history     = []
        st.session_state.pending_image    = None
        st.session_state.pending_img_type = None
        st.session_state.pending_img_name = None
        st.session_state.trigger_prompt   = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# BACKEND IMPORT
# ═══════════════════════════════════════════════════════════════════════════
from backend.agent import get_chatbot_response

# ═══════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-logo">{svg('plane', 18, '#ffffff')}</div>
        <span class="topbar-title">Travel Assistant</span>
        <span class="topbar-label">Beta</span>
    </div>
    <div class="topbar-right">
        {svg('compass', 13, '#8890aa')}
        &nbsp;Plan &middot; Explore &middot; Discover
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# WELCOME STATE
# ═══════════════════════════════════════════════════════════════════════════
SUGGESTIONS = [
    "Plan a 7-day Japan itinerary",
    "Best beaches in Southeast Asia",
    "Visa requirements for Schengen",
    "Hidden gems in Morocco",
]

if not st.session_state.chat_history:
    st.markdown(f"""
    <div class="welcome">
        <div class="welcome-icon">{svg('globe', 34, '#ffffff')}</div>
        <h2>Where to next?</h2>
        <p>Ask me anything about travel -- itineraries, landmarks,
           visa info, or upload an image for AI identification.</p>
    </div>
    """, unsafe_allow_html=True)

    for suggestion in SUGGESTIONS:
        if st.button(suggestion, key=f"chip_{suggestion[:10]}"):
            st.session_state.trigger_prompt = suggestion
            st.rerun()

    st.write("")


# ═══════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════════════════════
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.markdown(
                f'<div class="attached-preview">'
                f'<img src="data:{message["image_type"]};base64,{message["image"]}" />'
                f'</div>',
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════════════════════════════════════
# IMAGE ATTACHMENT
# ═══════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(
        f'<div class="attach-label">'
        f'{svg("paperclip", 14, "#7c74ff")}'
        f'<span style="font-weight:600; color:#c8cde0">Identify a landmark or OCR a document</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    uploaded_image = st.file_uploader(
        "Attach image for AI",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key=f"img_uploader_{st.session_state.uploader_key}"
    )

    if uploaded_image is not None:
        uploaded_image.seek(0)
        raw = uploaded_image.read()
        st.session_state.pending_image    = base64.b64encode(raw).decode("utf-8")
        st.session_state.pending_img_type = uploaded_image.type
        st.session_state.pending_img_name = uploaded_image.name

if st.session_state.pending_image:
    c_preview, c_close = st.columns([10, 1])
    with c_preview:
        st.markdown(
            f'<div class="thumb-strip">'
            f'<img src="data:{st.session_state.pending_img_type};base64,'
            f'{st.session_state.pending_image}" />'
            f'<span>{st.session_state.pending_img_name}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c_close:
        if st.button("X", key="remove_img_main"):
            st.session_state.pending_image    = None
            st.session_state.pending_img_type = None
            st.session_state.pending_img_name = None
            st.session_state.uploader_key += 1
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# CHAT INPUT
# ═══════════════════════════════════════════════════════════════════════════
user_prompt = st.chat_input("Ask about a destination, request an itinerary...")

if st.session_state.trigger_prompt:
    user_prompt = st.session_state.trigger_prompt
    st.session_state.trigger_prompt = None


# ═══════════════════════════════════════════════════════════════════════════
# MESSAGE SUBMISSION
# ═══════════════════════════════════════════════════════════════════════════
if user_prompt:
    user_msg = {"role": "user", "content": user_prompt}

    if st.session_state.pending_image:
        user_msg["image"]      = st.session_state.pending_image
        user_msg["image_type"] = st.session_state.pending_img_type
        st.session_state.pending_image    = None
        st.session_state.pending_img_type = None
        st.session_state.pending_img_name = None
        st.session_state.uploader_key += 1

    st.session_state.chat_history.append(user_msg)
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# AI RESPONSE
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(
            '<div class="typing-dots">'
            '<span></span><span></span><span></span>'
            '</div>',
            unsafe_allow_html=True
        )

        ai_response = get_chatbot_response(st.session_state.chat_history)
        placeholder.markdown(ai_response)

    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    st.rerun()
