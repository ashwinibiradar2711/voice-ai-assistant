"""Streamlit UI for the Voice AI Assistant.

Run with:  streamlit run app.py
"""

import hashlib

import streamlit as st

from voice_assistant.assistant import EmptyAudioError, Turn, VoiceAssistant
from voice_assistant.config import settings
from voice_assistant.languages import DEFAULT, LANGUAGES
from voice_assistant.llm import build_llm
from voice_assistant.stt import build_stt
from voice_assistant.tts import build_tts

st.set_page_config(page_title="Voice AI Assistant", page_icon="🎙️", layout="centered")


@st.cache_resource(show_spinner="Loading speech models...")
def get_components():
    return build_stt(settings), build_llm(settings), build_tts(settings)


def get_assistant() -> VoiceAssistant:
    if "assistant" not in st.session_state:
        stt, llm, tts = get_components()
        st.session_state.assistant = VoiceAssistant(stt, llm, tts)
        st.session_state.chat = []  # list of dicts for display
        st.session_state.last_audio = None
    return st.session_state.assistant


def add_turn(turn: Turn) -> None:
    st.session_state.chat.append({"role": "user", "content": turn.transcript, "lang": turn.language.name})
    st.session_state.chat.append({
        "role": "assistant",
        "content": turn.reply,
        "audio": turn.speech.audio if turn.speech else None,
        "mime": turn.speech.mime if turn.speech else None,
        "timings": turn.timings_ms,
        "total": turn.total_ms,
    })


assistant = get_assistant()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    speak = st.toggle("Speak replies aloud", value=True)
    st.caption(
        f"**Speech-to-text:** Whisper `{settings.stt_model}` ({settings.stt_provider})  \n"
        f"**LLM:** `{settings.llm_model}`  \n"
        f"**Text-to-speech:** {'Edge neural voices' if settings.tts_provider == 'edge' else 'offline voice'}"
    )
    st.caption("Languages: " + ", ".join(lang.name for lang in LANGUAGES.values()))
    if st.button("🗑️ New conversation"):
        assistant.reset()
        st.session_state.chat = []
        st.rerun()

# ---------- Main ----------
st.title("🎙️ Voice AI Assistant")
st.caption("Speak your question and hear the answer. Speech → Whisper → LLM → neural voice.")

if not settings.api_key:
    st.warning("No API_KEY found. Copy `.env.example` to `.env` and add your Groq key.")

for i, msg in enumerate(st.session_state.chat):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "user":
            st.caption(f"🌐 {msg['lang']}")
        else:
            if msg.get("audio"):
                is_latest = i == len(st.session_state.chat) - 1
                st.audio(msg["audio"], format=msg["mime"], autoplay=is_latest)
            t = msg["timings"]
            st.caption(
                "⏱️ " + " · ".join(f"{k.replace('_', ' ')} {v} ms" for k, v in t.items())
                + f" · **total {msg['total']} ms**"
            )

recording = st.audio_input("🎤 Tap to record your question")
typed = st.chat_input("...or type a message")

try:
    if recording is not None:
        data = recording.getvalue()
        digest = hashlib.md5(data).hexdigest()
        if digest != st.session_state.last_audio:  # don't re-process on reruns
            st.session_state.last_audio = digest
            with st.spinner("Listening and thinking..."):
                add_turn(assistant.process_audio(data, "question.wav", speak=speak))
            st.rerun()
    if typed:
        with st.spinner("Thinking..."):
            add_turn(assistant.process_text(typed, DEFAULT, speak=speak))
        st.rerun()
except EmptyAudioError as e:
    st.info(str(e))
except Exception as e:  # show the problem instead of crashing the app
    st.error(f"Something went wrong: {e}")
