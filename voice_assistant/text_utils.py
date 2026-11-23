"""Clean LLM text so it sounds natural when spoken aloud."""

import re

_EMOJI = re.compile(
    "[\U0001f300-\U0001faff\U00002600-\U000027bf\U0001f000-\U0001f2ff️]", flags=re.UNICODE
)


def clean_for_speech(text: str) -> str:
    """Remove markdown, links, code and emojis that a TTS voice would read out literally."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)  # code blocks
    text = re.sub(r"`([^`]*)`", r"\1", text)  # inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"https?://\S+", "", text)  # bare urls
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)  # headings
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)  # bullet markers
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)  # numbered lists
    text = re.sub(r"(\*\*|__|\*|_|~~)", "", text)  # bold / italic / strike
    text = _EMOJI.sub("", text)
    text = re.sub(r"\s*\n\s*", " ", text)  # one line
    return re.sub(r"\s{2,}", " ", text).strip()


def truncate_for_speech(text: str, max_chars: int = 900) -> str:
    """Cut long text at a sentence end so the spoken reply stays short."""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "), cut.rfind("।"))
    return cut[: end + 1].strip() if end > max_chars // 2 else cut.rsplit(" ", 1)[0] + "..."
