"""Project Idea Generator - LLM mini project.
Input: domain, skill level, time -> prompt LLM for 5 ideas -> show as cards.
"""
import json
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-2.5-flash"

PROMPT_TEMPLATE = """You are a friendly project mentor for final-year engineering students.

Student profile:
- Domain / interest: {domain}
- Skill level: {level}
- Time available: {weeks} week(s)

Suggest exactly 5 DIFFERENT project ideas that a student of this level can finish
in the given time. Keep each scope realistic (no model training from scratch).

Return ONLY a JSON array (no markdown, no extra text). Each item must have:
"title": short catchy name,
"description": 2 sentences on what it does and who it helps,
"scope": what is included in the time limit and what is left out,
"tools": list of 3-6 tools/libraries/APIs,
"modules": list of 3-5 modules to build (e.g. "Input form", "Prompt builder"),
"difficulty": one of "Easy", "Medium", "Hard",
"estimated_days": integer
"""

BADGE = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}


def build_prompt(domain: str, level: str, weeks: int) -> str:
    return PROMPT_TEMPLATE.format(domain=domain.strip(), level=level, weeks=weeks)


def generate_ideas(prompt: str) -> list[dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found. Add it to your .env file.")
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0.9
        ),
    )
    text = resp.text.strip().replace("```json", "").replace("```", "").strip()
    ideas = json.loads(text)
    if isinstance(ideas, dict):  # model wrapped the list in an object
        ideas = next(iter(ideas.values()))
    return ideas


def show_card(i: int, idea: dict) -> None:
    diff = idea.get("difficulty", "Medium")
    with st.container(border=True):
        st.subheader(f"{i}. {idea.get('title', 'Untitled')}")
        st.caption(
            f"{BADGE.get(diff, '⚪')} {diff}  •  ⏱ ~{idea.get('estimated_days', '?')} days"
        )
        st.write(idea.get("description", ""))
        st.markdown(f"**Scope:** {idea.get('scope', '')}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🛠 Tools**")
            for t in idea.get("tools", []):
                st.markdown(f"- {t}")
        with c2:
            st.markdown("**📦 Modules**")
            for m in idea.get("modules", []):
                st.markdown(f"- {m}")


st.set_page_config(page_title="Project Idea Generator", page_icon="💡", layout="centered")
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

dark_mode = st.toggle("Dark mode", key="dark_mode")
theme = {
    "page": "#11101a" if dark_mode else "#fbfaff",
    "page_end": "#171522" if dark_mode else "#fffaf4",
    "ink": "#f4f1ff" if dark_mode else "#18152b",
    "muted": "#b2adc6" if dark_mode else "#716d87",
    "card": "rgba(31, 29, 45, 0.94)" if dark_mode else "rgba(255, 255, 255, 0.88)",
    "form": "rgba(30, 28, 44, 0.92)" if dark_mode else "rgba(255, 255, 255, 0.82)",
    "field": "#211f30" if dark_mode else "#fcfbff",
    "border": "rgba(191, 176, 255, 0.18)" if dark_mode else "rgba(118, 87, 255, 0.12)",
    "field_border": "#49445f" if dark_mode else "#e8e4f2",
    "glow_pink": "rgba(135, 57, 104, 0.25)" if dark_mode else "rgba(255, 201, 229, 0.55)",
    "glow_purple": "rgba(86, 66, 163, 0.30)" if dark_mode else "rgba(183, 174, 255, 0.48)",
    "shadow": "rgba(0, 0, 0, 0.24)" if dark_mode else "rgba(72, 60, 116, 0.10)",
}
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

    :root {
        --ink: __INK__;
        --muted: __MUTED__;
        --purple: #7657ff;
        --pink: #ff70a6;
        --card: __CARD__;
        --form: __FORM__;
        --field: __FIELD__;
        --border: __BORDER__;
        --field-border: __FIELD_BORDER__;
        --shadow: __SHADOW__;
    }

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
        color: var(--ink);
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 5%, __GLOW_PINK__, transparent 24rem),
            radial-gradient(circle at 92% 18%, __GLOW_PURPLE__, transparent 22rem),
            linear-gradient(180deg, __PAGE__ 0%, __PAGE_END__ 100%);
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    #MainMenu, footer, header { visibility: hidden; }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stWidgetLabel"] p, label, [data-testid="stMarkdownContainer"] {
        color: var(--ink);
    }

    [data-testid="stToggle"] { justify-content: flex-end; }

    .hero {
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.75rem;
        border: 1px solid var(--border);
        border-radius: 999px;
        background: var(--card);
        color: #a998ff;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        box-shadow: 0 8px 30px rgba(88, 69, 150, 0.08);
    }

    .hero h1 {
        margin: 0.75rem 0 0.45rem;
        font-family: "Manrope", sans-serif;
        font-size: clamp(2.35rem, 7vw, 4.3rem);
        line-height: 1;
        letter-spacing: -0.055em;
    }

    .hero h1 span {
        background: linear-gradient(100deg, #7657ff 10%, #ff70a6 82%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .hero p {
        max-width: 590px;
        margin: 0 auto;
        color: var(--muted);
        font-size: 1.05rem;
        line-height: 1.65;
    }

    [data-testid="stForm"] {
        padding: 1.15rem;
        border: 1px solid var(--border);
        border-radius: 24px;
        background: var(--form);
        box-shadow: 0 18px 50px var(--shadow);
        backdrop-filter: blur(16px);
    }

    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] input {
        border-radius: 14px !important;
        border-color: var(--field-border) !important;
        background: var(--field) !important;
        color: var(--ink) !important;
    }

    [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
        background: linear-gradient(90deg, #7657ff, #ff70a6);
    }

    .stButton button, [data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 52px;
        border: 0;
        border-radius: 15px;
        background: linear-gradient(100deg, #7657ff 0%, #9d71ff 55%, #ff70a6 120%);
        color: white;
        font-weight: 800;
        box-shadow: 0 12px 28px rgba(118, 87, 255, 0.25);
        transition: transform 160ms ease, box-shadow 160ms ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 32px rgba(118, 87, 255, 0.32);
        color: white;
        border: 0;
    }

    [data-testid="stContainer"] {
        border: 1px solid var(--border) !important;
        border-radius: 22px !important;
        background: var(--card);
        box-shadow: 0 14px 38px var(--shadow);
    }

    [data-testid="stContainer"] [data-testid="stMarkdownContainer"] h2 {
        font-family: "Manrope", sans-serif;
        letter-spacing: -0.025em;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    .results-heading {
        margin: 2.1rem 0 0.65rem;
        font-family: "Manrope", sans-serif;
        font-size: 1.55rem;
        letter-spacing: -0.03em;
    }

    @media (max-width: 640px) {
        .block-container { padding: 1rem 1rem 3rem; }
        [data-testid="stForm"] { padding: 0.85rem; border-radius: 18px; }
        .hero p { font-size: 0.98rem; }
    }
    </style>
    """
    .replace("__INK__", theme["ink"])
    .replace("__MUTED__", theme["muted"])
    .replace("__CARD__", theme["card"])
    .replace("__FORM__", theme["form"])
    .replace("__FIELD__", theme["field"])
    .replace("__BORDER__", theme["border"])
    .replace("__FIELD_BORDER__", theme["field_border"])
    .replace("__SHADOW__", theme["shadow"])
    .replace("__GLOW_PINK__", theme["glow_pink"])
    .replace("__GLOW_PURPLE__", theme["glow_purple"])
    .replace("__PAGE__", theme["page"])
    .replace("__PAGE_END__", theme["page_end"]),
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">✦ build mode: on</div>
        <h1>Find your next <span>big idea.</span></h1>
        <p>Share what you’re into, your experience, and how much time you have. Get five realistic project ideas you can build and show off.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("A few quick details help us tailor the ideas to you.")
with st.form("idea_form", clear_on_submit=False):
    domain = st.text_input(
        "What are you interested in?",
        placeholder="e.g. music, climate, gaming, healthcare",
        help="A broad topic is totally fine. You can mention a specific problem too.",
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        level = st.selectbox(
            "How experienced are you?",
            ["Beginner", "Intermediate", "Advanced"],
            help="Choose the level that feels closest; ideas will be scoped accordingly.",
        )
    with c2:
        weeks = st.slider(
            "How much time do you have?",
            1,
            12,
            2,
            help="Pick the number of weeks you can spend building your project.",
            format="%d weeks",
        )

    submitted = st.form_submit_button("✨  Find my project ideas")

if submitted:
    if not domain.strip():
        st.warning("Tell us at least one thing you’re interested in, and we’ll take it from there.")
    else:
        with st.spinner("Finding ideas that fit your vibe and timeline..."):
            try:
                ideas = generate_ideas(build_prompt(domain, level, weeks))
                st.session_state["ideas"] = ideas
                st.success("Your ideas are ready. Pick one that sparks your curiosity!")
            except json.JSONDecodeError:
                st.error("We couldn’t format the ideas this time. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

ideas = st.session_state.get("ideas", [])
if ideas:
    st.markdown('<div class="results-heading">Your project lineup <span>✦</span></div>', unsafe_allow_html=True)
    for start in range(0, len(ideas), 2):
        cols = st.columns(2)
        for offset, idea in enumerate(ideas[start:start + 2]):
            with cols[offset]:
                show_card(start + offset + 1, idea)
