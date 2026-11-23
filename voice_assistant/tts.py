"""Text-to-speech: Microsoft Edge neural voices (free) or offline pyttsx3."""

import asyncio
import os
import tempfile
from dataclasses import dataclass
from typing import Protocol

from voice_assistant.languages import Language


@dataclass
class Speech:
    audio: bytes
    mime: str  # "audio/mpeg" or "audio/wav"


class TextToSpeech(Protocol):
    def synthesize(self, text: str, language: Language) -> Speech: ...


class EdgeTTS:
    """Natural neural voices via the edge-tts library. Free, no API key, needs internet."""

    def __init__(self, rate: str = "+0%"):
        import edge_tts  # noqa: F401  (fail early if not installed)

        self.rate = rate

    async def _synthesize(self, text: str, voice: str) -> bytes:
        import edge_tts

        chunks = []
        async for chunk in edge_tts.Communicate(text, voice, rate=self.rate).stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)

    def synthesize(self, text: str, language: Language) -> Speech:
        return Speech(asyncio.run(self._synthesize(text, language.voice)), "audio/mpeg")


class OfflineTTS:
    """pyttsx3 uses the operating system's built-in voices (SAPI5 on Windows). Fully offline."""

    def synthesize(self, text: str, language: Language) -> Speech:
        import pyttsx3

        engine = pyttsx3.init()
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            engine.save_to_file(text, path)
            engine.runAndWait()
            with open(path, "rb") as f:
                return Speech(f.read(), "audio/wav")
        finally:
            os.remove(path)


def build_tts(settings) -> TextToSpeech:
    if settings.tts_provider == "offline":
        return OfflineTTS()
    return EdgeTTS()
