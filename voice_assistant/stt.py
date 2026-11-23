"""Speech-to-text: Whisper on Groq (cloud) or faster-whisper (local CPU)."""

import io
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Transcript:
    text: str
    language: str | None  # code or name reported by Whisper


class SpeechToText(Protocol):
    def transcribe(self, audio: bytes, filename: str = "audio.wav") -> Transcript: ...


class GroqWhisperSTT:
    """Whisper large-v3-turbo through Groq's OpenAI-compatible audio API."""

    def __init__(self, base_url: str, api_key: str, model: str):
        from openai import OpenAI

        self.client = OpenAI(base_url=base_url, api_key=api_key or "missing-key")
        self.model = model

    def transcribe(self, audio: bytes, filename: str = "audio.wav") -> Transcript:
        result = self.client.audio.transcriptions.create(
            model=self.model,
            file=(filename, audio),
            response_format="verbose_json",  # includes the detected language
        )
        return Transcript(text=(result.text or "").strip(), language=getattr(result, "language", None))


class LocalWhisperSTT:
    """faster-whisper running fully offline on the CPU (int8 quantised)."""

    def __init__(self, model_size: str = "base"):
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio: bytes, filename: str = "audio.wav") -> Transcript:
        segments, info = self.model.transcribe(io.BytesIO(audio), vad_filter=True)
        text = " ".join(s.text.strip() for s in segments)
        return Transcript(text=text.strip(), language=info.language)


def build_stt(settings) -> SpeechToText:
    if settings.stt_provider == "local":
        return LocalWhisperSTT(settings.local_whisper_size)
    return GroqWhisperSTT(settings.api_base_url, settings.api_key, settings.stt_model)
