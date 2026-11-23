"""The voice pipeline: audio -> STT -> LLM -> TTS -> audio, with per-stage timings."""

import time
from dataclasses import dataclass, field

from voice_assistant.languages import Language, resolve_language
from voice_assistant.llm import ChatModel
from voice_assistant.stt import SpeechToText
from voice_assistant.text_utils import clean_for_speech, truncate_for_speech
from voice_assistant.tts import Speech, TextToSpeech


class EmptyAudioError(ValueError):
    """Raised when no speech could be recognised in the recording."""


@dataclass
class Turn:
    transcript: str
    language: Language
    reply: str
    speech: Speech | None
    timings_ms: dict[str, int] = field(default_factory=dict)

    @property
    def total_ms(self) -> int:
        return sum(self.timings_ms.values())


class VoiceAssistant:
    """Orchestrates the three models. Components are injected, so each can be swapped or faked."""

    def __init__(self, stt: SpeechToText, llm: ChatModel, tts: TextToSpeech | None):
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.history: list[dict] = []

    def process_audio(self, audio: bytes, filename: str = "audio.wav", speak: bool = True) -> Turn:
        if not audio:
            raise EmptyAudioError("The recording is empty.")
        t0 = time.perf_counter()
        transcript = self.stt.transcribe(audio, filename)
        stt_ms = _ms(t0)
        if not transcript.text:
            raise EmptyAudioError("I couldn't hear any speech. Please try again closer to the mic.")
        turn = self.process_text(transcript.text, resolve_language(transcript.language), speak)
        turn.timings_ms = {"speech_to_text": stt_ms, **turn.timings_ms}
        return turn

    def process_text(self, text: str, language: Language, speak: bool = True) -> Turn:
        t0 = time.perf_counter()
        reply = clean_for_speech(self.llm.reply(text, language.name, self.history))
        timings = {"llm": _ms(t0)}

        speech = None
        if speak and self.tts and reply:
            t1 = time.perf_counter()
            speech = self.tts.synthesize(truncate_for_speech(reply), language)
            timings["text_to_speech"] = _ms(t1)

        self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
        return Turn(text, language, reply, speech, timings)

    def reset(self) -> None:
        self.history.clear()


def _ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)
