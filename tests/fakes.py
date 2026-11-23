"""Fake components so the pipeline can be tested without models or internet."""

from voice_assistant.stt import Transcript
from voice_assistant.tts import Speech


class FakeSTT:
    def __init__(self, text="What is AI?", language="english"):
        self.text, self.language = text, language
        self.calls = 0

    def transcribe(self, audio, filename="audio.wav"):
        self.calls += 1
        return Transcript(self.text, self.language)


class FakeLLM:
    def __init__(self, reply="**AI** means *artificial intelligence*."):
        self.reply_text = reply
        self.seen = []

    def reply(self, user_text, language, history):
        self.seen.append((user_text, language, list(history)))
        return self.reply_text


class FakeTTS:
    def __init__(self):
        self.spoken = []

    def synthesize(self, text, language):
        self.spoken.append((text, language.voice))
        return Speech(b"MP3DATA", "audio/mpeg")
