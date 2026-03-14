import streamlit as st
import os
import sys
import base64
from dotenv import load_dotenv

# Load environment variables before any backend imports
load_dotenv()

# Allow Python to resolve the backend package (one level above this file)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TripMind AI",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Defaults ─────────────────────────────────────────────────────
if "chat_history"     not in st.session_state: st.session_state.chat_history     = []
if "theme"            not in st.session_state: st.session_state.theme            = "light"
if "pending_image"    not in st.session_state: st.session_state.pending_image    = None
if "pending_img_type" not in st.session_state: st.session_state.pending_img_type = None
if "pending_img_name" not in st.session_state: st.session_state.pending_img_name = None
if "trigger_prompt"   not in st.session_state: st.session_state.trigger_prompt   = None
if "uploader_key"     not in st.session_state: st.session_state.uploader_key     = 0

IS_DARK = st.session_state.theme == "dark"

# ── Design Token Palette ───────────────────────────────────────────────────────
DARK = dict(
    bg0="#0d0f1a", bg1="#141624", bg2="#1c1f30", bg3="#242840",
    border="#2e324e", border2="#3b4060",
    txt0="#e8eaf6",  # very bright for dark bg
    txt1="#b0b8d8",  # secondary
    txt2="#6b7299",  # muted
    accent="#5b8dee", accent2="#3d6fdb", accent_glow="rgba(91,141,238,0.15)",
    user_bg="#1a2340", user_border="#2a3860",
    success="#34d399", error="#f87171", warn="#fbbf24",
    card_shadow="0 2px 16px rgba(0,0,0,0.45)",
    msg_shadow="0 1px 8px rgba(0,0,0,0.3)",
)
LIGHT = dict(
    bg0="#f0f2f8", bg1="#ffffff", bg2="#ffffff", bg3="#eef1f8",
    border="#dde2f0", border2="#c5ccde",
    txt0="#0d0f1a",  # near-black
    txt1="#3a4060",  # secondary
    txt2="#7a82a0",  # muted
    accent="#3b68e8", accent2="#2a52c9", accent_glow="rgba(59,104,232,0.10)",
    user_bg="#eef2fd", user_border="#c0caef",
    success="#059669", error="#dc2626", warn="#d97706",
    card_shadow="0 2px 16px rgba(30,40,90,0.08)",
    msg_shadow="0 1px 8px rgba(30,40,90,0.06)",
)
T = DARK if IS_DARK else LIGHT

# ── Inline SVG Icon helper ─────────────────────────────────────────────────────
def svg(name, size=18, color="currentColor"):
    """Returns a minimal inline SVG icon string."""
    s = str(size)
    paths = {
        "globe":      f'<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2c-2.667 3.333-4 6.667-4 10s1.333 6.667 4 10M12 2c2.667 3.333 4 6.667 4 10s-1.333 6.667-4 10"/>',
        "plane":      f'<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21 4 21 4s-2 0-3.5 1.5L14 9 5.8 6.2l-2.06 2.06 6.38 3.19L6.39 15l-1.95-.65L3 15.76l3.5 1.5L8 20.5l1.44-1.44L8.8 17.2l3.74-3.74 3.19 6.38 2.06-2.06z"/>',
        "map":        f'<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>',
        "paperclip":  f'<path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>',
        "db":         f'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        "clear":      f'<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>',
        "sun":        f'<circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/><line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/>',
        "moon":       f'<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    }
    p = paths.get(name, "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{p}</svg>')


# ── CSS Refinement ──
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── Global Reset ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
}}

/* ── App background with premium gradient ── */
.stApp {{
    background: radial-gradient(circle at 50% -20%, {T['bg3']} 0%, {T['bg0']} 80%) !important;
    background-attachment: fixed !important;
    color: {T['txt0']} !important;
}}

/* ── Hide Streamlit chrome ── */
[data-testid="stDecoration"], [data-testid="stToolbar"], footer {{ visibility: hidden !important; }}
[data-testid="stHeader"] {{ 
    background: transparent !important;
}}

/* ═══════════════════════════════════════
   MAIN CONTAINER
═══════════════════════════════════════ */
.block-container {{
    padding: 1.5rem 2rem !important;
    max-width: 850px !important;
    margin: 0 auto !important;
    transition: all 0.3s ease;
}}

/* ═══════════════════════════════════════
   TOP BAR / NAV
═══════════════════════════════════════ */
.topbar {{
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.75rem;
    background: {T['bg1']}aa;
    backdrop-filter: blur(20px);
    border-bottom: 1px solid {T['border']};
    margin: -1.5rem -2rem 2rem -2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}}
.topbar-left {{ display: flex; align-items: center; gap: 0.7rem; }}
.topbar-title {{
    font-size: 17px;
    font-weight: 800;
    color: {T['txt0']};
    letter-spacing: -0.5px;
}}
.topbar-badge {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: {T['accent']};
    background: {T['accent_glow']};
    border: 1px solid {T['accent']}33;
    border-radius: 6px;
    padding: 0.1rem 0.45rem;
}}
.topbar-right {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 13px;
    color: {T['txt2']};
    font-weight: 500;
}}

/* ═══════════════════════════════════════
   SIDEBAR REFINEMENT
═══════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: {T['bg1']} !important;
    border-right: 1px solid {T['border']} !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}

/* Sidebar text color fix */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {{
    color: {T['txt1']} !important;
}}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {{
    background: {T['bg3']} !important;
    color: {T['txt0']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    margin-bottom: 6px !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {T['accent']} !important;
    color: white !important;
    border-color: {T['accent']} !important;
}}
.welcome {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 1rem 2rem;
    text-align: center;
}}
.welcome-icon {{
    width: 72px; height: 72px;
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    border-radius: 22px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 2rem;
    box-shadow: 0 15px 35px {T['accent']}44;
    transform: rotate(-4deg);
    transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}}
.welcome-icon:hover {{
    transform: rotate(0deg) scale(1.05);
}}
.welcome h2 {{
    font-size: 36px;
    font-weight: 800;
    color: {T['txt0']};
    letter-spacing: -1.2px;
    margin-bottom: 0.75rem;
}}
.welcome p {{
    font-size: 16px;
    color: {T['txt2']};
    max-width: 440px;
    line-height: 1.6;
    margin-bottom: 3rem;
}}

/* ═══════════════════════════════════════
   CHIPS (SUGGESTIONS)
   Aggressive targeting to ensure horizontal centering & wrapping
═══════════════════════════════════════ */
/* Target the parent container of the chips area */
[data-testid="stVerticalBlock"] > div:has(button[key^="chip_"]) {{
    display: inline-block !important;
    width: auto !important;
    margin: 0.35rem !important;
}}

/* Ensure the wrapper of all chips is centered */
div:has(> div > div > button[key^="chip_"]) {{
    text-align: center !important;
    display: block !important;
    width: 100% !important;
    margin-top: 1rem !important;
}}

.block-container .stButton > button {{
    background: {T['bg2']} !important;
    color: {T['txt1']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 99px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    white-space: nowrap !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}}

.block-container .stButton > button:hover {{
    background: {T['accent']} !important;
    border-color: {T['accent']} !important;
    color: #ffffff !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 15px {T['accent']}33 !important;
}}

/* ═══════════════════════════════════════
   CHATS & UI
═══════════════════════════════════════ */
[data-testid="stChatMessage"] {{
    background: {T['bg1']}cc !important;
    backdrop-filter: blur(10px);
    border: 1px solid {T['border']} !important;
    border-radius: 18px !important;
    box-shadow: {T['msg_shadow']} !important;
}}

/* User specific message tint */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: {T['user_bg']}cc !important;
    border-color: {T['user_border']} !important;
}}

/* Chat Input Bar */
[data-testid="stChatInput"] {{
    border-radius: 20px !important;
    border: 1.5px solid {T['border']} !important;
    background: {T['bg1']} !important;
    padding: 4px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
}}

/* File Uploader Theme Fix (Dark Mode Support) */
[data-testid="stFileUploaderDropzone"] {{
    background-color: {T['bg2']} !important;
    border: 1.5px dashed {T['border2']} !important;
    border-radius: 12px !important;
    transition: all 0.2s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {T['accent']} !important;
    background-color: {T['bg3']} !important;
}}
[data-testid="stFileUploaderDropzone"] p, 
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] div {{
    color: {T['txt1']} !important;
}}
/* Sidebar specific uploader tweak */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
    padding: 0.5rem !important;
}}

/* Hide the native Streamlit file list to avoid redundancy with our custom preview */
[data-testid="stFileUploaderFileList"] {{
    display: none !important;
}}

/* ═══════════════════════════════════════
   MOBILE ADJUSTMENTS
═══════════════════════════════════════ */
@media (max-width: 768px) {{
    .welcome h2 {{ font-size: 28px; }}
    .welcome {{ padding: 3rem 1rem 1.5rem; }}
    .welcome-icon {{ width: 60px; height: 60px; }}
    .block-container .stButton > button {{
        padding: 0.45rem 1rem !important;
        font-size: 13px !important;
    }}
}}

/* ═══════════════════════════════════════
   CHAT MESSAGES
   We let Streamlit render the chat containers natively and style them via CSS.
   We do NOT inject message text inside raw HTML — markdown is rendered by st.markdown().
═══════════════════════════════════════ */
[data-testid="stChatMessage"] {{
    background: {T['bg2']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.8rem !important;
    box-shadow: {T['msg_shadow']} !important;
    animation: msgIn 0.22s ease both;
}}
@keyframes msgIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* User message — tinted background */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: {T['user_bg']} !important;
    border-color: {T['user_border']} !important;
}}

/* Chat message text must be readable in both themes */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{
    color: {T['txt0']} !important;
    font-size: 14.5px !important;
    line-height: 1.7 !important;
}}
[data-testid="stChatMessage"] strong {{
    color: {T['txt0']} !important;
    font-weight: 600 !important;
}}
[data-testid="stChatMessage"] code {{
    background: {T['bg3']} !important;
    color: {T['accent']} !important;
    border-radius: 4px !important;
    padding: 0.1em 0.35em !important;
    font-size: 13px !important;
}}
[data-testid="stChatMessage"] pre {{
    background: {T['bg3']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
}}

/* ── Custom avatar circles ── */
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessageAvatarUser"] {{
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']}) !important;
    border-radius: 50% !important;
    border: none !important;
}}
[data-testid="stChatMessageAvatarUser"] {{
    background: {T['bg3']} !important;
    border: 1.5px solid {T['border2']} !important;
}}

/* ── Main area file uploader (image attach) — theme-aware ── */
.block-container [data-testid="stFileUploaderDropzone"] {{
    background: {T['bg2']} !important;
    border: 1.5px dashed {T['border2']} !important;
    border-radius: 10px !important;
    color: {T['txt1']} !important;
}}
.block-container [data-testid="stFileUploaderDropzone"] p,
.block-container [data-testid="stFileUploaderDropzone"] span {{
    color: {T['txt2']} !important;
}}
.block-container [data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {T['accent']} !important;
}}
.block-container [data-testid="stFileUploaderDropzone"] button {{
    background: {T['bg3']} !important;
    color: {T['txt1']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 6px !important;
}}

/* ── Typing dots animation ── */
.typing-dots {{
    display: flex; align-items: center; gap: 5px; padding: 4px 0;
}}
.typing-dots span {{
    display: inline-block; width: 7px; height: 7px;
    border-radius: 50%; background: {T['accent']};
    animation: tdot 1.2s infinite ease-in-out;
}}
.typing-dots span:nth-child(2) {{ animation-delay: 0.18s; }}
.typing-dots span:nth-child(3) {{ animation-delay: 0.36s; }}
@keyframes tdot {{
    0%, 80%, 100% {{ transform: scale(0.65); opacity: 0.4; }}
    40%           {{ transform: scale(1.1);  opacity: 1; }}
}}

/* ═══════════════════════════════════════
   ATTACHMENT AREA (above chat input)
═══════════════════════════════════════ */
.attach-label {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 12.5px;
    color: {T['txt2']};
    padding: 0.25rem 0 0.35rem;
}}
.thumb-strip {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: {T['user_bg']};
    border: 1px solid {T['user_border']};
    border-radius: 8px;
    padding: 0.35rem 0.65rem;
    font-size: 12.5px;
    color: {T['txt1']};
    font-weight: 500;
    margin-bottom: 0.4rem;
    width: fit-content;
}}
.thumb-strip img {{
    width: 24px; height: 24px;
    border-radius: 4px;
    object-fit: cover;
}}
.attached-preview img {{
    border-radius: 10px;
    border: 1px solid {T['border']};
    max-width: 300px;
    margin-top: 0.5rem;
    display: block;
}}

/* ═══════════════════════════════════════
   CHAT INPUT BAR
═══════════════════════════════════════ */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {{
    background-color: {T['bg0']} !important;
}}
[data-testid="stChatInput"] {{
    padding: 0 !important;
    background: transparent !important;
    margin-bottom: 2rem !important;
}}
[data-testid="stChatInput"] > div {{
    background-color: {T['bg2']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
    box-shadow: {T['card_shadow']} !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
[data-testid="stChatInput"] > div:focus-within {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_glow']} !important;
}}
[data-testid="stChatInput"] textarea {{
    background-color: transparent !important;
    border: none !important;
    color: {T['txt0']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14.5px !important;
    caret-color: {T['accent']} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {T['txt2']} !important;
}}
[data-testid="stChatInputSubmitButton"] {{
    background: {T['accent']} !important;
    border-radius: 8px !important;
}}
[data-testid="stChatInputSubmitButton"]:hover {{
    background: {T['accent2']} !important;
}}

/* ═══════════════════════════════════════
   SIDEBAR CUSTOM COMPONENTS
═══════════════════════════════════════ */
.sb-brand {{
    display: flex; align-items: center; gap: 0.6rem;
    padding: 1.25rem 1.25rem 1rem;
    border-bottom: 1px solid {T['border']};
}}
.sb-brand-name {{
    font-size: 15px; font-weight: 800;
    color: {T['txt0']} !important;
    letter-spacing: -0.2px;
}}
.sb-brand-sub {{
    font-size: 11px;
    color: {T['txt2']} !important;
}}
.sb-icon {{
    width: 34px; height: 34px;
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']});
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}}
.sb-section {{
    padding: 1rem 1.25rem 0.25rem;
}}
.sb-label {{
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: {T['txt2']} !important;
    margin-bottom: 0.5rem;
    display: block;
}}
.status-pill {{
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.45rem 0.7rem;
    background: {T['bg3']};
    border: 1px solid {T['border']};
    border-radius: 8px;
    font-size: 13px;
    color: {T['txt1']} !important;
    margin-bottom: 0.3rem;
}}
.sdot {{
    width: 7px; height: 7px;
    border-radius: 50%; flex-shrink: 0;
}}
.sdot-green  {{ background: {T['success']}; animation: sdot-pulse 2s infinite; }}
.sdot-red    {{ background: {T['error']}; }}
.sdot-yellow {{ background: {T['warn']}; }}
@keyframes sdot-pulse {{
    0%,100% {{ box-shadow: 0 0 0 0 {T['success']}55; }}
    50%     {{ box-shadow: 0 0 0 3px transparent; }}
}}
.spill {{
    margin-left: auto; font-size: 11px; font-weight: 600;
    padding: 0.1rem 0.45rem; border-radius: 99px;
}}
.spill-ok   {{ color: {T['success']}; background: {T['success']}20; }}
.spill-warn {{ color: {T['warn']};    background: {T['warn']}20; }}
.spill-err  {{ color: {T['error']};   background: {T['error']}20; }}
.sb-sep {{ border: none; border-top: 1px solid {T['border']}; margin: 0.75rem 0; }}

/* Alerts & spinner */
.stAlert {{ border-radius: 8px !important; font-size: 13px !important; }}
.stSpinner > div {{ border-top-color: {T['accent']} !important; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Brand header ──
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-icon">{svg('globe', 19, '#ffffff')}</div>
        <div>
            <div class="sb-brand-name">TripMind AI</div>
            <div class="sb-brand-sub">Powered by Gemini</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Appearance ──
    st.markdown('<div class="sb-section"><span class="sb-label">Appearance</span></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Light", key="btn_light", use_container_width=True):
                st.session_state.theme = "light"
                st.rerun()
        with c2:
            if st.button("Dark", key="btn_dark", use_container_width=True):
                st.session_state.theme = "dark"
                st.rerun()

    st.markdown('<hr class="sb-sep">', unsafe_allow_html=True)

    # ── System Status ──
    st.markdown('<div class="sb-section"><span class="sb-label">System Status</span></div>', unsafe_allow_html=True)

    google_api_key    = os.getenv("GOOGLE_API_KEY")
    langsmith_api_key = os.getenv("LANGCHAIN_API_KEY")
    tavily_api_key    = os.getenv("TAVILY_API_KEY")

    gemini_ok  = bool(google_api_key    and google_api_key    != "your_google_api_key_here")
    tracing_ok = bool(langsmith_api_key and langsmith_api_key != "your_langsmith_api_key_here")
    search_ok  = bool(tavily_api_key    and tavily_api_key    != "your_tavily_api_key_here")

    def status_pill(label, ok, warn=False):
        """Renders an HTML status row with a coloured dot and badge."""
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

    # ── Knowledge Base ──
    st.markdown('<div class="sb-section"><span class="sb-label">Knowledge Base</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12.5px;color:{T["txt2"]};padding:0 1.25rem 0.6rem;line-height:1.5;">'
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
                st.error(f"Cannot save — close **{uploaded_doc.name}** first.")

    st.markdown('<div style="padding:0 1.25rem 0.5rem;">', unsafe_allow_html=True)
    from backend.rag import ingest_documents
    if st.button("Build Knowledge Base", use_container_width=True, key="btn_build"):
        with st.spinner("Indexing documents..."):
            if ingest_documents():
                st.success("Knowledge base ready.")
            else:
                st.warning("No documents found — upload a file first.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-sep">', unsafe_allow_html=True)

    # ── Session ──
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


# ══════════════════════════════════════════════════════════════════════════════
# BACKEND IMPORT
# ══════════════════════════════════════════════════════════════════════════════
from backend.agent import get_chatbot_response

# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        {svg('plane', 19, T['accent'])}
        <span class="topbar-title">Travel Assistant</span>
        <span class="topbar-badge">Beta</span>
    </div>
    <div class="topbar-right">
        {svg('map', 14, T['txt2'])}
        &nbsp;Plan &middot; Explore &middot; Discover
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# WELCOME / EMPTY STATE  (only shown when chat is empty)
# ══════════════════════════════════════════════════════════════════════════════
SUGGESTIONS = [
    "Plan a 7-day Japan itinerary",
    "Best beaches in Southeast Asia",
    "Visa requirements for Schengen",
    "Hidden gems in Morocco",
]

if not st.session_state.chat_history:
    st.markdown(f"""
    <div class="welcome">
        <div class="welcome-icon">{svg('globe', 32, '#ffffff')}</div>
        <h2>Where to next?</h2>
        <p>Ask me anything about travel — itineraries, landmarks,
           visa info, or upload an image for AI identification.</p>
    </div>
    """, unsafe_allow_html=True)

    # Render chips in a group that our CSS will target and wrap
    # Each chip will be an inline-block element centered via CSS
    for suggestion in SUGGESTIONS:
        if st.button(suggestion, key=f"chip_{suggestion[:10]}"):
            st.session_state.trigger_prompt = suggestion
            st.rerun()

    st.write("")  # spacing


# ══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ── IMPORTANT: We use st.chat_message() + st.markdown() natively.
#    We never embed message content inside raw HTML strings.
#    This ensures markdown (bold, lists, code blocks) renders correctly.
# ══════════════════════════════════════════════════════════════════════════════
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        # Render message text as markdown — Streamlit handles all formatting
        st.markdown(message["content"])

        # Render attached image if present (stored as base64)
        if "image" in message:
            st.markdown(
                f'<div class="attached-preview">'
                f'<img src="data:{message["image_type"]};base64,{message["image"]}" />'
                f'</div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE ATTACH  (Only shown when chat is empty or for the first message)
# ══════════════════════════════════════════════════════════════════════════════
# ── IMAGE ATTACHMENT AREA ──
# This is always available above the chat input for landmark identification
with st.container():
    st.markdown(
        f'<div class="attach-label">'
        f'{svg("paperclip", 14, T["accent"])}'
        f'<span style="font-weight:600; color:{T["txt1"]}">Identify a landmark or OCR a document</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    uploaded_image = st.file_uploader(
        "Attach image for AI",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key=f"img_uploader_{st.session_state.uploader_key}"
    )

    # When a new image is picked, stage it in session state
    if uploaded_image is not None:
        uploaded_image.seek(0)
        raw = uploaded_image.read()
        st.session_state.pending_image    = base64.b64encode(raw).decode("utf-8")
        st.session_state.pending_img_type = uploaded_image.type
        st.session_state.pending_img_name = uploaded_image.name

# Show thumbnail strip + remove button when an image is staged
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
        if st.button("✕", key="remove_img_main"):
            st.session_state.pending_image    = None
            st.session_state.pending_img_type = None
            st.session_state.pending_img_name = None
            st.session_state.uploader_key += 1
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
user_prompt = st.chat_input("Ask about a destination, request an itinerary…")

# Suggestion chips pre-fill the input via session state trigger
if st.session_state.trigger_prompt:
    user_prompt = st.session_state.trigger_prompt
    st.session_state.trigger_prompt = None


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGE SUBMISSION
# When user sends a message:
#   1. Build the message dict
#   2. Attach staged image if present, then clear staging
#   3. Append to history and re-run (so message renders before AI responds)
# ══════════════════════════════════════════════════════════════════════════════
if user_prompt:
    user_msg = {"role": "user", "content": user_prompt}

    if st.session_state.pending_image:
        user_msg["image"]      = st.session_state.pending_image
        user_msg["image_type"] = st.session_state.pending_img_type
        st.session_state.pending_image    = None
        st.session_state.pending_img_type = None
        st.session_state.pending_img_name = None
        st.session_state.uploader_key += 1  # Reset the uploader widget

    st.session_state.chat_history.append(user_msg)
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# AI RESPONSE
# Triggered after re-run when the last message is from the user.
# Shows a typing-dots animation while the backend generates the response,
# then replaces it with the real markdown content.
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    with st.chat_message("assistant"):
        # Show animated typing indicator while model is working
        placeholder = st.empty()
        placeholder.markdown(
            '<div class="typing-dots">'
            '<span></span><span></span><span></span>'
            '</div>',
            unsafe_allow_html=True
        )

        # Call the backend — passes full history for multi-turn context
        ai_response = get_chatbot_response(st.session_state.chat_history)

        # Replace typing dots with the actual response
        placeholder.markdown(ai_response)

    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    st.rerun()
