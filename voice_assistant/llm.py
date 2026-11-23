"""Chat model with a voice-friendly system prompt and short-term memory."""

from typing import Protocol

SYSTEM_PROMPT = """You are a friendly, helpful voice assistant. Your replies are converted to \
speech, so:
- Answer in 1 to 4 short, natural sentences, as if speaking.
- Never use markdown, bullet points, tables, code blocks, emojis or URLs.
- Reply in the SAME language as the user ({language}).
- If you are not sure about a fact, say so honestly instead of guessing.
- For questions needing live data (weather, news, prices), explain that you don't have \
internet access."""


class ChatModel(Protocol):
    def reply(self, user_text: str, language: str, history: list[dict]) -> str: ...


def build_messages(user_text: str, language: str, history: list[dict], history_turns: int) -> list[dict]:
    """System prompt + the most recent conversation turns + the new user message."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(language=language)}]
    if history_turns > 0:
        messages += [{"role": m["role"], "content": m["content"]} for m in history[-history_turns:]]
    messages.append({"role": "user", "content": user_text})
    return messages


class GroqChatModel:
    """Any OpenAI-compatible chat endpoint (Groq by default; OpenAI, Ollama also work)."""

    def __init__(self, base_url: str, api_key: str, model: str, temperature: float,
                 max_tokens: int, history_turns: int, reasoning_effort: str = ""):
        from openai import OpenAI

        self.client = OpenAI(base_url=base_url, api_key=api_key or "missing-key")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        self.history_turns = history_turns

    def reply(self, user_text: str, language: str, history: list[dict]) -> str:
        kwargs = {
            "model": self.model,
            "messages": build_messages(user_text, language, history, self.history_turns),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.reasoning_effort:  # only for reasoning models such as gpt-oss
            kwargs["reasoning_effort"] = self.reasoning_effort
        response = self.client.chat.completions.create(**kwargs)
        return (response.choices[0].message.content or "").strip()


def build_llm(settings) -> ChatModel:
    return GroqChatModel(settings.api_base_url, settings.api_key, settings.llm_model,
                         settings.temperature, settings.max_tokens, settings.history_turns,
                         settings.reasoning_effort)
