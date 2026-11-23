"""Application settings, read from environment variables (or a .env file)."""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass


@dataclass(frozen=True)
class Settings:
    # One Groq key is used for both speech-to-text (Whisper) and the LLM.
    api_base_url: str = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
    api_key: str = os.getenv("API_KEY", "")

    # Speech-to-text: "groq" (Whisper in the cloud) or "local" (faster-whisper on your CPU)
    stt_provider: str = os.getenv("STT_PROVIDER", "groq")
    stt_model: str = os.getenv("STT_MODEL", "whisper-large-v3-turbo")
    local_whisper_size: str = os.getenv("LOCAL_WHISPER_SIZE", "base")

    # Language model
    llm_model: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
    temperature: float = float(os.getenv("TEMPERATURE", "0.6"))
    # Reasoning models (gpt-oss) spend tokens "thinking", so allow enough room.
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1024"))
    # "low" / "medium" / "high" for reasoning models; leave empty for other models.
    reasoning_effort: str = os.getenv("REASONING_EFFORT", "low")
    history_turns: int = int(os.getenv("HISTORY_TURNS", "6"))

    # Text-to-speech: "edge" (free neural voices, needs internet) or "offline" (pyttsx3)
    tts_provider: str = os.getenv("TTS_PROVIDER", "edge")


settings = Settings()
