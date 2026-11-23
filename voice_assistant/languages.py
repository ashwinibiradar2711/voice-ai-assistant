"""Language detection results -> language code and a matching neural voice."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    code: str  # ISO 639-1, e.g. "en"
    name: str  # e.g. "English"
    voice: str  # Microsoft Edge neural voice id


LANGUAGES: dict[str, Language] = {
    "en": Language("en", "English", "en-IN-NeerjaNeural"),
    "hi": Language("hi", "Hindi", "hi-IN-SwaraNeural"),
    "mr": Language("mr", "Marathi", "mr-IN-AarohiNeural"),
    "kn": Language("kn", "Kannada", "kn-IN-SapnaNeural"),
    "ta": Language("ta", "Tamil", "ta-IN-PallaviNeural"),
    "te": Language("te", "Telugu", "te-IN-ShrutiNeural"),
    "gu": Language("gu", "Gujarati", "gu-IN-DhwaniNeural"),
    "bn": Language("bn", "Bengali", "bn-IN-TanishaaNeural"),
    "es": Language("es", "Spanish", "es-ES-ElviraNeural"),
    "fr": Language("fr", "French", "fr-FR-DeniseNeural"),
    "de": Language("de", "German", "de-DE-KatjaNeural"),
}

DEFAULT = LANGUAGES["en"]

# Whisper may report a full name ("english") or a code ("en").
_BY_NAME = {lang.name.lower(): lang for lang in LANGUAGES.values()}


def resolve_language(value: str | None) -> Language:
    """Map a Whisper language result (code or name, any case) to a Language."""
    if not value:
        return DEFAULT
    key = value.strip().lower()
    return LANGUAGES.get(key) or _BY_NAME.get(key) or DEFAULT
