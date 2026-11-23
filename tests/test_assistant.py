import pytest

from tests.fakes import FakeLLM, FakeSTT, FakeTTS
from voice_assistant.assistant import EmptyAudioError, VoiceAssistant
from voice_assistant.languages import LANGUAGES


def make(stt=None, llm=None, tts=None):
    stt, llm, tts = stt or FakeSTT(), llm or FakeLLM(), tts or FakeTTS()
    return VoiceAssistant(stt, llm, tts), stt, llm, tts


def test_full_pipeline_returns_transcript_reply_and_audio():
    va, stt, llm, tts = make()
    turn = va.process_audio(b"wav-bytes")
    assert turn.transcript == "What is AI?"
    assert turn.language.code == "en"
    assert turn.reply == "AI means artificial intelligence."  # markdown removed
    assert turn.speech.audio == b"MP3DATA"
    assert set(turn.timings_ms) == {"speech_to_text", "llm", "text_to_speech"}
    assert turn.total_ms >= 0


def test_reply_language_follows_detected_language():
    va, _, llm, tts = make(stt=FakeSTT("नमस्ते", "hindi"))
    turn = va.process_audio(b"x")
    assert turn.language.code == "hi"
    assert llm.seen[0][1] == "Hindi"
    assert tts.spoken[0][1] == LANGUAGES["hi"].voice


def test_history_is_kept_and_passed_to_llm():
    va, _, llm, _ = make()
    va.process_text("first", LANGUAGES["en"])
    va.process_text("second", LANGUAGES["en"])
    _, _, history_at_second_call = llm.seen[1]
    assert [m["content"] for m in history_at_second_call][0] == "first"
    assert len(va.history) == 4


def test_reset_clears_history():
    va, *_ = make()
    va.process_text("hello", LANGUAGES["en"])
    va.reset()
    assert va.history == []


def test_speak_false_skips_tts():
    va, _, _, tts = make()
    turn = va.process_text("hi", LANGUAGES["en"], speak=False)
    assert turn.speech is None
    assert tts.spoken == []
    assert "text_to_speech" not in turn.timings_ms


def test_works_without_tts_component():
    va = VoiceAssistant(FakeSTT(), FakeLLM(), None)
    assert va.process_text("hi", LANGUAGES["en"]).speech is None


def test_empty_audio_raises():
    va, *_ = make()
    with pytest.raises(EmptyAudioError):
        va.process_audio(b"")


def test_silence_raises_and_does_not_call_llm():
    va, _, llm, _ = make(stt=FakeSTT(text=""))
    with pytest.raises(EmptyAudioError):
        va.process_audio(b"silence")
    assert llm.seen == []
