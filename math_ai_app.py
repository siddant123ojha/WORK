import streamlit as st
import google.generativeai as genai
import base64
import json
import re
import io
from PIL import Image

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MathAI Student",
    page_icon="∑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GEMINI SETUP ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ✅ FREE TIER MODELS ONLY — as of March 2026
# ──────────────────────────────────────────────────────────
# gemini-2.5-flash        → FREE: 10 req/min, 250 req/day  ✅ (used here)
# gemini-2.5-pro          → FREE: 5 req/min,  100 req/day  ✅
# gemini-2.5-flash-lite   → FREE: 15 req/min, 1000 req/day ✅
# ──────────────────────────────────────────────────────────
# gemini-3.1-pro-preview  → ❌ NO FREE TIER (limit=0) — paid only
# gemini-1.5-flash        → ❌ DEPRECATED March 2026
# gemini-2.0-flash        → ❌ RETIRED March 3, 2026
# ──────────────────────────────────────────────────────────
# ⚠️  IMPORTANT: quotas are per PROJECT, not per API key.
#     Creating a new API key in the same Google project
#     does NOT reset your quota — create a new project instead.
# ──────────────────────────────────────────────────────────
GEMINI_TEXT_MODEL   = "gemini-2.5-flash"
GEMINI_VISION_MODEL = "gemini-2.5-flash"  # handles both text + vision/images

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide default streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Dark background */
.stApp { background: #0a0e1a; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1422 !important;
    border-right: 1px solid #1e2535;
}
[data-testid="stSidebar"] * { color: #8892a4 !important; }
[data-testid="stSidebar"] .stRadio label { 
    font-size: 14px !important; 
    padding: 6px 0 !important;
}

/* Cards */
.ai-card {
    background: #0f1422;
    border: 1px solid #1e2535;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
}

.ai-card-accent {
    background: linear-gradient(135deg, #0f1e3d, #111827);
    border: 1px solid #2255aa44;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
}

/* Headings */
h1, h2, h3 { color: #e4eaf5 !important; }
.page-title {
    font-size: 22px;
    font-weight: 600;
    color: #e4eaf5;
    margin-bottom: 4px;
}
.page-sub {
    font-size: 13px;
    color: #4a5568;
    margin-bottom: 20px;
}

/* Stats row */
.stat-row { display: flex; gap: 12px; margin-bottom: 16px; }
.stat-box {
    flex: 1;
    background: #0f1422;
    border: 1px solid #1e2535;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.stat-val { font-size: 22px; font-weight: 600; }
.stat-lbl { font-size: 11px; color: #4a5568; margin-top: 2px; }

/* Step cards */
.step-card {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    padding: 12px 0;
    border-bottom: 1px solid #1e2535;
}
.step-num {
    width: 26px; height: 26px;
    border-radius: 50%;
    background: #1a3a6e;
    color: #60a5fa;
    font-size: 12px; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-label { font-size: 11px; color: #4a5568; margin-bottom: 3px; }
.step-math { font-family: 'DM Mono', monospace; font-size: 14px; color: #e4eaf5; }
.step-math .hl { color: #fb923c; }

/* Chat bubbles */
.chat-user {
    background: #1a3a6e22;
    border: 1px solid #2255aa33;
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    font-size: 14px;
    color: #c3cfe8;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
}
.chat-ai {
    background: #0f1422;
    border: 1px solid #1e2535;
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px;
    font-size: 14px;
    color: #c3cfe8;
    margin: 8px 0;
    max-width: 85%;
}

/* Gemini badge */
.gemini-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 9px;
    background: #1a3a6e22;
    border: 1px solid #2255aa33;
    border-radius: 20px;
    font-size: 11px;
    color: #60a5fa;
    margin-bottom: 10px;
}

/* Chips */
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.chip {
    padding: 5px 12px;
    background: #1e2535;
    border: 1px solid #2a3347;
    border-radius: 20px;
    font-size: 12px;
    color: #8892a4;
    cursor: pointer;
}

/* Image result box */
.img-result {
    background: #0a0e1a;
    border: 1px solid #1e2535;
    border-radius: 12px;
    overflow: hidden;
}

/* Camera section */
.camera-box {
    background: #0f1422;
    border: 2px dashed #1e2535;
    border-radius: 14px;
    padding: 28px;
    text-align: center;
    margin-bottom: 14px;
}
.camera-icon { font-size: 36px; margin-bottom: 8px; }
.camera-text { font-size: 14px; color: #4a5568; }

/* Progress bars */
.prog-item { margin-bottom: 12px; }
.prog-label-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; }
.prog-bar-bg { background: #1e2535; border-radius: 4px; height: 6px; overflow: hidden; }
.prog-bar { height: 100%; border-radius: 4px; }

/* Input overrides */
.stTextInput input, .stTextArea textarea {
    background: #0a0e1a !important;
    border: 1px solid #1e2535 !important;
    color: #e4eaf5 !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 14px !important;
}
.stButton button {
    background: #1a3a6e !important;
    color: #60a5fa !important;
    border: 1px solid #2255aa55 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}
.stButton button:hover {
    background: #1f6feb !important;
    color: white !important;
}

/* Selectbox */
.stSelectbox select {
    background: #0a0e1a !important;
    border: 1px solid #1e2535 !important;
    color: #e4eaf5 !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1422;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #4a5568;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background: #1a3a6e !important;
    color: #60a5fa !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 16px; }

/* Graph area */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }

/* Level badges */
.level-all { color: #a78bfa; background: #4c1d9522; border: 1px solid #6d28d944; border-radius: 20px; padding: 3px 10px; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "text": "👋 Hello! I'm your MathAI tutor powered by Gemini. I can help students of **all levels** — from basic arithmetic to university-level calculus. Ask me anything! 🎓"}
    ]
if "solved_today" not in st.session_state:
    st.session_state.solved_today = 0


# ── HELPER: FRIENDLY ERROR PARSER ────────────────────────────────────────────
def _friendly_error(e: Exception) -> str:
    msg = str(e)
    if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
        return (
            "⏳ **Rate limit reached.** Your free tier quota has been used up.\n\n"
            "**Fix options:**\n"
            "- Wait until midnight Pacific Time for daily quota reset\n"
            "- Or go to [AI Studio](https://aistudio.google.com) → enable billing for Tier 1\n\n"
            "_Free tier: gemini-2.5-flash = 10 req/min · 250 req/day_"
        )
    if "API_KEY" in msg or "api key" in msg.lower() or "invalid" in msg.lower():
        return "🔑 **Invalid API key.** Check your key in the sidebar."
    if "not found" in msg.lower() or "does not exist" in msg.lower():
        return f"❌ **Model not found:** `{GEMINI_TEXT_MODEL}`. Check available models at AI Studio."
    return f"❌ **Error:** {msg}"


# ── HELPER: GEMINI TEXT ───────────────────────────────────────────────────────
import time

def ask_gemini(prompt: str, system: str = "") -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Please add your GEMINI_API_KEY to the sidebar or `.streamlit/secrets.toml`."
    for attempt in range(2):
        try:
            model = genai.GenerativeModel(GEMINI_TEXT_MODEL)
            full  = f"{system}\n\n{prompt}" if system else prompt
            resp  = model.generate_content(full)
            return resp.text
        except Exception as e:
            if attempt == 0 and "429" not in str(e):
                time.sleep(2)
                continue
            return _friendly_error(e)
    return "Unexpected error — please try again."


# ── HELPER: GEMINI VISION (image + text) ─────────────────────────────────────
def ask_gemini_vision(prompt: str, image: Image.Image) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Please add your GEMINI_API_KEY to the sidebar or `.streamlit/secrets.toml`."
    try:
        model = genai.GenerativeModel(GEMINI_VISION_MODEL)
        resp  = model.generate_content([prompt, image])
        return resp.text
    except Exception as e:
        return _friendly_error(e)


# ── HELPER: GEMINI IMAGE GEN ──────────────────────────────────────────────────
def generate_image_gemini(prompt: str):
    if not GEMINI_API_KEY:
        return None, "⚠️ Please add your GEMINI_API_KEY."
    try:
        model  = genai.ImageGenerationModel("imagen-3.0-generate-002")
        result = model.generate_images(prompt=prompt, number_of_images=1)
        return result.images[0]._pil_image, None
    except Exception as e:
        msg = str(e)
        if "billing" in msg.lower() or "403" in msg or "permission" in msg.lower():
            return None, (
                "🔒 **Imagen requires a paid Google Cloud account.**\n\n"
                "Enable billing at [Google Cloud Console](https://console.cloud.google.com) "
                "to unlock Imagen. All other tabs work on the free tier!"
            )
        return None, _friendly_error(e)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ∑ MathAI Student")
    st.markdown('<span class="level-all">✦ All Levels</span>', unsafe_allow_html=True)
    st.markdown("---")

    api_key_input = st.text_input("🔑 Gemini API Key", type="password",
                                   value=GEMINI_API_KEY,
                                   placeholder="AIza...")
    if api_key_input:
        GEMINI_API_KEY = api_key_input
        genai.configure(api_key=GEMINI_API_KEY)

    st.markdown("---")
    st.markdown("**📚 Topics**")
    topic = st.radio("", ["🔵 Algebra", "🟣 Calculus", "🟢 Geometry",
                           "🟠 Statistics", "🔴 Trigonometry",
                           "⚪ Number Theory", "🔷 Linear Algebra"],
                     label_visibility="collapsed")

    st.markdown("---")
    st.caption("Powered by Google Gemini API")
    st.caption("Built with Streamlit 🎈")


# ── MAIN HEADER ───────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="page-title">∑ MathAI Student</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">AI-powered math tutor for all levels · Powered by Google Gemini</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown('<div style="text-align:right; padding-top:8px"><span class="gemini-badge">⬥ Gemini API Active</span></div>', unsafe_allow_html=True)

# Stats row
st.markdown(f"""
<div class="stat-row">
  <div class="stat-box"><div class="stat-val" style="color:#60a5fa">{st.session_state.solved_today}</div><div class="stat-lbl">Solved Today</div></div>
  <div class="stat-box"><div class="stat-val" style="color:#34d399">5</div><div class="stat-lbl">Topics Available</div></div>
  <div class="stat-box"><div class="stat-val" style="color:#a78bfa">All</div><div class="stat-lbl">Student Levels</div></div>
  <div class="stat-box"><div class="stat-val" style="color:#fb923c">Flash</div><div class="stat-lbl">Gemini Model</div></div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧮 Math Solver",
    "💬 Q&A Chat",
    "📷 Camera",
    "🎨 Image Gen",
    "📈 Grapher"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MATH SOLVER
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Step-by-Step Math Solver")
    st.markdown("Enter any math problem and Gemini will break it down step by step.")

    level = st.select_slider("Student Level",
        options=["Primary", "Middle School", "High School", "University"],
        value="High School")

    expr = st.text_input("Math Problem",
        value="2x² + 5x - 3 = 0",
        placeholder="e.g. integrate x^2 from 0 to 3, solve 3x+2=11, find the derivative of sin(x)cos(x)...")

    st.markdown("**Quick examples:**")
    cols_ex = st.columns(5)
    examples = ["∫ x² dx", "lim x→0 sin(x)/x", "3x + 2y = 12", "√(144) + 5!", "sin²θ + cos²θ"]
    for i, col in enumerate(cols_ex):
        if col.button(examples[i], key=f"ex_{i}"):
            expr = examples[i]

    if st.button("✦ Solve with Gemini", use_container_width=True):
        if expr.strip():
            with st.spinner("Gemini is solving..."):
                system_prompt = f"""You are an expert math tutor helping a {level} student.
Solve the math problem step by step. Return ONLY valid JSON with this structure:
{{
  "problem_type": "short type name",
  "difficulty": "Easy/Medium/Hard",
  "steps": [
    {{"step": 1, "title": "Step title", "work": "Mathematical work shown", "explanation": "Why we do this"}},
    ...
  ],
  "final_answer": "The final answer",
  "tip": "A helpful tip or insight for this type of problem"
}}
No markdown, no code fences, just raw JSON."""

                raw = ask_gemini(expr, system_prompt)
                st.session_state.solved_today += 1

                # Try to parse JSON
                try:
                    clean = re.sub(r"```json|```", "", raw).strip()
                    data = json.loads(clean)

                    st.markdown(f"""
<div class="ai-card">
  <div class="gemini-badge">⬥ Gemini · {data.get('problem_type','Solution')} · {data.get('difficulty','')}</div>
  <div style="font-family:'DM Mono',monospace; font-size:15px; color:#60a5fa; margin-bottom:14px">
    {expr}
  </div>
""", unsafe_allow_html=True)

                    for s in data.get("steps", []):
                        st.markdown(f"""
<div class="step-card">
  <div class="step-num">{s['step']}</div>
  <div>
    <div class="step-label">{s['title']}</div>
    <div class="step-math">{s['work']}</div>
    <div style="font-size:12px; color:#4a5568; margin-top:4px">{s.get('explanation','')}</div>
  </div>
</div>""", unsafe_allow_html=True)

                    st.markdown(f"""
  <div style="margin-top:14px; padding:12px 16px; background:#0a2a1a; border:1px solid #16533344; border-radius:8px;">
    <div style="font-size:11px; color:#34d399; margin-bottom:4px">FINAL ANSWER</div>
    <div style="font-family:'DM Mono',monospace; font-size:16px; color:#6ee7b7">{data.get('final_answer','')}</div>
  </div>
  <div style="margin-top:10px; padding:10px 14px; background:#1a1a0a; border:1px solid #44440022; border-radius:8px; font-size:13px; color:#fbbf24">
    💡 {data.get('tip','')}
  </div>
</div>""", unsafe_allow_html=True)

                except Exception:
                    # Fallback: just display raw response nicely
                    st.markdown(f'<div class="ai-card"><div class="gemini-badge">⬥ Gemini</div><div style="font-size:14px;color:#c3cfe8;white-space:pre-wrap">{raw}</div></div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a math problem first.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Q&A CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### AI Math Tutor Chat")
    st.markdown("Ask any math question — Gemini will explain clearly for your level.")

    chat_level = st.selectbox("My level", ["Primary School", "Middle School", "High School", "University"], index=2, key="chat_level")

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai"><span class="gemini-badge">⬥ MathAI</span><br>{msg["text"]}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Suggested questions
    st.markdown("**Quick questions:**")
    q_cols = st.columns(3)
    quick_qs = [
        "What is a derivative?",
        "Explain the Pythagorean theorem",
        "How do I solve a quadratic?",
        "What is pi (π)?",
        "What are complex numbers?",
        "Explain integration"
    ]
    for i, col in enumerate(q_cols):
        if col.button(quick_qs[i], key=f"qq_{i}"):
            user_q = quick_qs[i]
            st.session_state.chat_history.append({"role": "user", "text": user_q})
            with st.spinner("Thinking..."):
                sys_p = f"You are a friendly, encouraging math tutor. The student is at {chat_level} level. Give clear, concise explanations with a simple example. Use plain text, no markdown."
                answer = ask_gemini(user_q, sys_p)
                st.session_state.chat_history.append({"role": "ai", "text": answer})
            st.rerun()

    user_input = st.text_input("Your question", placeholder="e.g. What does the derivative of a function represent?", key="chat_input")

    col_send, col_clear = st.columns([4, 1])
    with col_send:
        if st.button("Send →", use_container_width=True, key="send_btn"):
            if user_input.strip():
                st.session_state.chat_history.append({"role": "user", "text": user_input})
                with st.spinner("Gemini is thinking..."):
                    sys_p = f"You are a friendly, encouraging math tutor. The student is at {chat_level} level. Give clear explanations with examples when helpful."
                    answer = ask_gemini(user_input, sys_p)
                    st.session_state.chat_history.append({"role": "ai", "text": answer})
                st.rerun()
    with col_clear:
        if st.button("Clear", use_container_width=True, key="clear_btn"):
            st.session_state.chat_history = [st.session_state.chat_history[0]]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CAMERA / IMAGE INPUT
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📷 Solve from Photo")
    st.markdown("Take a photo or upload an image of your math question — Gemini Vision will read and solve it.")

    cam_level = st.selectbox("My level", ["Primary School", "Middle School", "High School", "University"], index=2, key="cam_level")

    source = st.radio("Image source", ["📷 Camera", "📁 Upload file"], horizontal=True)

    img_input = None

    if source == "📷 Camera":
        cam_img = st.camera_input("Point camera at your math problem")
        if cam_img:
            img_input = Image.open(cam_img)
    else:
        uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp", "heic"],
                                     label_visibility="collapsed")
        if uploaded:
            img_input = Image.open(uploaded)

    if img_input:
        st.image(img_input, caption="Your problem", use_column_width=True)

        extra = st.text_input("Additional context (optional)",
                              placeholder="e.g. This is a quadratic equation question from my homework")

        if st.button("🔍 Solve this problem with Gemini Vision", use_container_width=True):
            with st.spinner("Gemini is reading and solving your problem..."):
                vision_prompt = f"""You are an expert math tutor for a {cam_level} student.
Look at this image carefully. It contains a math problem or question.

1. First, READ and TRANSCRIBE the math problem exactly as written.
2. Then SOLVE it step by step, showing all working.
3. Give the final answer clearly.
4. Add a helpful tip at the end.

{f'Additional context from student: {extra}' if extra else ''}

Be thorough but clear. Use plain text."""

                answer = ask_gemini_vision(vision_prompt, img_input)
                st.session_state.solved_today += 1

            st.markdown(f"""
<div class="ai-card-accent">
  <div class="gemini-badge">⬥ Gemini Vision · Problem detected from image</div>
  <div style="font-size:14px; color:#c3cfe8; white-space:pre-wrap; line-height:1.7; margin-top:8px">{answer}</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown("""
<div class="camera-box">
  <div class="camera-icon">📐</div>
  <div class="camera-text">Point your camera at any math problem<br>
  Works with: handwritten questions, textbook problems, worksheets, exam papers</div>
</div>
""", unsafe_allow_html=True)

        st.info("📱 **Tip:** Works best with good lighting. Ensure the entire problem is visible in frame.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI IMAGE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🎨 Math Visual Generator")
    st.markdown("Generate visual diagrams and illustrations to help understand math concepts.")

    img_prompt = st.text_input("Describe the visual",
        value="A clear labeled diagram of a right triangle showing the Pythagorean theorem with color-coded sides",
        placeholder="e.g. A 3D graph of a parabola, Unit circle with labeled angles...")

    st.markdown("**Suggested visuals:**")
    sug_cols = st.columns(3)
    suggestions = [
        "Pythagorean theorem diagram with labeled sides",
        "Unit circle with all angles and coordinates",
        "3D surface plot of z = sin(x)cos(y)",
        "Venn diagram showing set union and intersection",
        "Number line showing negative and positive integers",
        "Geometric proof of the area of a circle"
    ]
    for i, col in enumerate(sug_cols):
        if col.button(suggestions[i][:30] + "...", key=f"sug_{i}"):
            img_prompt = suggestions[i]

    if st.button("✦ Generate with Gemini Imagen", use_container_width=True, key="gen_img"):
        with st.spinner("Generating image with Gemini Imagen..."):
            enhanced_prompt = f"Educational math diagram: {img_prompt}. Clean white background, clear labels, professional educational style, high resolution."
            pil_img, err = generate_image_gemini(enhanced_prompt)

        if pil_img:
            st.image(pil_img, caption=img_prompt, use_column_width=True)

            # Download button
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            st.download_button("⬇ Download Image", buf.getvalue(),
                               file_name="math_visual.png", mime="image/png")

            # Also explain the visual
            with st.spinner("Generating explanation..."):
                explanation = ask_gemini_vision(
                    "Describe this math diagram in simple terms. What concept does it show? How can it help a student understand the topic?",
                    pil_img
                )
            st.markdown(f'<div class="ai-card"><div class="gemini-badge">⬥ Gemini Explanation</div><div style="font-size:14px;color:#c3cfe8">{explanation}</div></div>',
                        unsafe_allow_html=True)
        elif err:
            st.error(err)
            st.info("💡 Gemini Imagen requires a paid Google Cloud account. In the meantime, the solver and Q&A features work with the free Gemini API.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — GRAPHING
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📈 Function Grapher")
    st.markdown("Plot any mathematical function and get AI analysis.")

    try:
        import numpy as np
        import plotly.graph_objects as go

        g_col1, g_col2 = st.columns([2, 1])

        with g_col1:
            func_input = st.text_input("Function f(x) =",
                value="np.sin(x) + 0.5*np.cos(2*x)",
                placeholder="e.g. x**2, np.sin(x), np.exp(-x**2)...")

            r_col1, r_col2 = st.columns(2)
            x_min = r_col1.number_input("x min", value=-6.28, step=0.5)
            x_max = r_col2.number_input("x max", value=6.28, step=0.5)

        with g_col2:
            graph_type = st.selectbox("Graph type", ["Line", "Scatter", "Area"])
            show_grid = st.checkbox("Show grid", value=True)
            show_zero = st.checkbox("Show zero lines", value=True)

        if st.button("📈 Plot Function", use_container_width=True):
            try:
                x = np.linspace(x_min, x_max, 500)
                y = eval(func_input)

                fig = go.Figure()

                color = "#60a5fa"
                if graph_type == "Line":
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines',
                        line=dict(color=color, width=2.5), name=f"f(x) = {func_input}"))
                elif graph_type == "Scatter":
                    fig.add_trace(go.Scatter(x=x[::5], y=y[::5], mode='markers',
                        marker=dict(color=color, size=4), name=f"f(x) = {func_input}"))
                elif graph_type == "Area":
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy',
                        fillcolor='rgba(96,165,250,0.15)',
                        line=dict(color=color, width=2), name=f"f(x) = {func_input}"))

                fig.update_layout(
                    plot_bgcolor='#0a0e1a',
                    paper_bgcolor='#0f1422',
                    font=dict(color='#8892a4', family='DM Sans'),
                    xaxis=dict(gridcolor='#1e2535' if show_grid else 'rgba(0,0,0,0)',
                               zerolinecolor='#2a3347' if show_zero else 'rgba(0,0,0,0)',
                               color='#4a5568'),
                    yaxis=dict(gridcolor='#1e2535' if show_grid else 'rgba(0,0,0,0)',
                               zerolinecolor='#2a3347' if show_zero else 'rgba(0,0,0,0)',
                               color='#4a5568'),
                    margin=dict(l=40, r=20, t=20, b=40),
                    height=340,
                    legend=dict(bgcolor='#0f1422', bordercolor='#1e2535', borderwidth=1)
                )

                st.plotly_chart(fig, use_container_width=True)

                # Stats
                s_cols = st.columns(4)
                s_cols[0].metric("Maximum", f"{float(np.max(y)):.4f}")
                s_cols[1].metric("Minimum", f"{float(np.min(y)):.4f}")
                s_cols[2].metric("Mean", f"{float(np.mean(y)):.4f}")
                s_cols[3].metric("Zeros ≈", str(int(np.sum(np.diff(np.sign(y)) != 0))))

                # AI analysis
                with st.spinner("Gemini analyzing your function..."):
                    analysis = ask_gemini(
                        f"Analyze the function f(x) = {func_input} on [{x_min}, {x_max}]. "
                        f"Briefly describe: domain, range, key features (zeros, extrema, symmetry, periodicity). "
                        f"Keep it concise, 3-4 sentences, plain text."
                    )
                st.markdown(f'<div class="ai-card"><div class="gemini-badge">⬥ Gemini Analysis</div><div style="font-size:14px;color:#c3cfe8">{analysis}</div></div>',
                            unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Could not evaluate function: {e}")
                st.info("💡 Use Python/NumPy syntax: `np.sin(x)`, `x**2`, `np.exp(x)`, `np.log(x)`")

    except ImportError:
        st.error("Please install: `pip install numpy plotly`")