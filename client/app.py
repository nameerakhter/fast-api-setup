# =============================================================================
# NATA 2026 Chatbot — Streamlit UI
# =============================================================================
#
# Calls FastAPI over HTTP (client never imports PyMongo / Gemini).
#
# Terminals:
#   1. cd server && uvicorn main:app --reload
#   2. cd client && streamlit run app.py
# =============================================================================

from __future__ import annotations

import streamlit as st

import api

st.set_page_config(
    page_title="NATA Chatbot",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SUGGESTED_QUESTIONS = {
    "en": [
        "What is the NATA 2026 application fee for General / OBC-NCL category in India?",
        "When is Phase 1 of NATA 2026 held, and what are the exam session timings?",
        "How many attempts are allowed in Phase 1 and Phase 2 for NATA 2026?",
        "Is there negative marking in NATA 2026?",
        "What is the NATA 2026 exam pattern — duration and total marks?",
        "Where can I contact the NATA Helpdesk or raise a ticket for application issues?",
    ],
    "hi": [
        "भारत में सामान्य और अन्य पिछड़ा वर्ग (गैर-क्रीमी लेयर / OBC-NCL) उम्मीदवारों के लिए NATA 2026 का आवेदन शुल्क कितना है?",
        "NATA 2026 का फेज़ 1 कब आयोजित होता है और परीक्षा सत्रों का समय क्या है?",
        "NATA 2026 में फेज़ 1 और फेज़ 2 में कितने प्रयास दिए जा सकते हैं?",
        "क्या NATA 2026 में नकारात्मक अंकन लागू होता है?",
        "NATA 2026 की परीक्षा का स्वरूप क्या है — कुल समय और कुल अंक?",
        "NATA हैल्पडेस्क से कैसे संपर्क करूँ या आवेदन से जुड़ी समस्याओं के लिए टिकट कहाँ से दर्ज करूँ?",
    ],
}

st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%); }
        .block-container { max-width: 720px; padding-top: 1.5rem; padding-bottom: 2rem; }
        .nata-header {
            display: flex; align-items: center; gap: 0.75rem;
            background: #ffffff; border: 1px solid #e2e8f0; border-radius: 1rem;
            padding: 0.85rem 1rem; margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }
        .nata-badge {
            width: 2.25rem; height: 2.25rem; border-radius: 0.5rem;
            background: #0f172a; color: #fff; display: flex; align-items: center;
            justify-content: center; font-weight: 700; font-size: 0.75rem;
        }
        .nata-title { font-weight: 650; color: #0f172a; font-size: 0.95rem; line-height: 1.25; }
        div[data-testid="stChatMessage"] { background: transparent; }
        div[data-testid="stButton"] button {
            text-align: left; height: auto; white-space: normal;
            padding: 0.75rem 0.9rem; border: 1px solid #e2e8f0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

for key, default in (
    ("lang", "en"),
    ("messages", []),
    ("session_id", None),
    ("history_loaded", False),
    ("pending_prompt", None),
):
    if key not in st.session_state:
        st.session_state[key] = default


def load_history() -> None:
    try:
        messages, session_id = api.get_messages(
            lang=st.session_state.lang,
            session_id=st.session_state.session_id,
        )
        st.session_state.session_id = session_id
        normalized = []
        for message in messages:
            role = message.get("role", "assistant")
            text = message.get("content") or ""
            if not text and message.get("parts"):
                text = "\n".join(
                    part.get("text", "")
                    for part in message["parts"]
                    if isinstance(part, dict)
                )
            if text.strip():
                normalized.append({"role": role, "content": text.strip()})
        st.session_state.messages = normalized
    except Exception as exc:
        st.warning(f"Could not load chat history: {exc}")
    finally:
        st.session_state.history_loaded = True


if not st.session_state.history_loaded:
    load_history()

st.markdown(
    """
    <div class="nata-header">
      <div class="nata-badge">NATA</div>
      <div class="nata-title">NATA (National Aptitude Test in Architecture)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_lang, col_new = st.columns([2, 1])
with col_lang:
    selected = st.radio(
        "Language / भाषा",
        options=["en", "hi"],
        format_func=lambda v: "English" if v == "en" else "हिन्दी",
        horizontal=True,
        label_visibility="collapsed",
        key="lang_radio",
    )
with col_new:
    if st.button("New chat", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.history_loaded = False
        st.session_state.pending_prompt = None
        st.rerun()

if selected != st.session_state.lang:
    st.session_state.lang = selected
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.history_loaded = False
    st.session_state.pending_prompt = None
    st.rerun()

lang = st.session_state.lang


def run_chat_turn(user_text: str) -> None:
    user_text = user_text.strip()
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    api_messages = [
        {
            "role": m["role"],
            "parts": [{"type": "text", "text": m["content"]}],
            "content": m["content"],
        }
        for m in st.session_state.messages
    ]
    session_out: dict = {}

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(
                api.stream_chat(
                    api_messages,
                    lang=lang,
                    session_id=st.session_state.session_id,
                    session_out=session_out,
                )
            )
            if session_out.get("session_id"):
                st.session_state.session_id = session_out["session_id"]
            st.session_state.messages.append(
                {"role": "assistant", "content": str(reply)}
            )
        except Exception as exc:
            error = f"Error: {exc}"
            st.error(error)
            st.session_state.messages.append({"role": "assistant", "content": error})


pending = st.session_state.pending_prompt
if pending:
    st.session_state.pending_prompt = None

show_empty = not st.session_state.messages and not pending
if show_empty:
    empty_title = "बातचीत शुरू करें" if lang == "hi" else "Start a conversation"
    empty_desc = (
        "नीचे लिखें या सुझाए गए प्रश्न में से कोई एक चुनें"
        if lang == "hi"
        else "Type below or tap a suggested NATA question"
    )
    st.subheader(empty_title)
    st.caption(empty_desc)

    cols = st.columns(2)
    for index, question in enumerate(SUGGESTED_QUESTIONS[lang]):
        with cols[index % 2]:
            if st.button(
                question,
                key=f"suggest-{lang}-{index}",
                use_container_width=True,
            ):
                st.session_state.pending_prompt = question
                st.rerun()
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

prompt = st.chat_input(
    "अपना प्रश्न लिखें..." if lang == "hi" else "Enter your question..."
)
if pending:
    run_chat_turn(pending)
elif prompt:
    run_chat_turn(prompt)
