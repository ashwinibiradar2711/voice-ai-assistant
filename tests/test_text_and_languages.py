import pytest

from voice_assistant.languages import DEFAULT, resolve_language
from voice_assistant.llm import SYSTEM_PROMPT, build_messages
from voice_assistant.text_utils import clean_for_speech, truncate_for_speech


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("**Bold** and *italic*", "Bold and italic"),
        ("# Title\nText", "Title Text"),
        ("- one\n- two", "one two"),
        ("1. first\n2. second", "first second"),
        ("See [docs](https://x.com) now", "See docs now"),
        ("Visit https://example.com today", "Visit today"),
        ("Use `pip install`", "Use pip install"),
        ("Great job 🎉👍", "Great job"),
    ],
)
def test_clean_for_speech(raw, expected):
    assert clean_for_speech(raw) == expected


def test_truncate_keeps_short_text():
    assert truncate_for_speech("Short.", 100) == "Short."


def test_truncate_cuts_at_sentence_end():
    text = "First sentence here. " * 20
    out = truncate_for_speech(text, 120)
    assert len(out) <= 120
    assert out.endswith(".")


@pytest.mark.parametrize(
    "value,code",
    [("en", "en"), ("English", "en"), ("hindi", "hi"), ("MR", "mr"), ("marathi", "mr"),
     ("klingon", "en"), (None, "en"), ("", "en")],
)
def test_resolve_language(value, code):
    assert resolve_language(value).code == code


def test_default_language_is_english():
    assert DEFAULT.code == "en"


def test_build_messages_has_language_and_trimmed_history():
    history = [{"role": "user", "content": f"m{i}"} for i in range(10)]
    msgs = build_messages("now", "Marathi", history, history_turns=4)
    assert msgs[0]["role"] == "system"
    assert "Marathi" in msgs[0]["content"]
    assert [m["content"] for m in msgs[1:-1]] == ["m6", "m7", "m8", "m9"]
    assert msgs[-1] == {"role": "user", "content": "now"}


def test_build_messages_without_history():
    msgs = build_messages("hi", "English", [{"role": "user", "content": "old"}], history_turns=0)
    assert len(msgs) == 2


def test_system_prompt_forbids_markdown():
    assert "markdown" in SYSTEM_PROMPT.lower()
