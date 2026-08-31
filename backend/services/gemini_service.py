import os
from collections.abc import Generator

from google import genai
from google.genai import types

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def _get_model() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _build_contents(history: list[dict], new_message: str) -> list[types.Content]:
    contents = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=new_message)]))
    return contents


def generate_reply(history: list[dict], message: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=_get_model(),
        contents=_build_contents(history, message),
    )
    return response.text or ""


def stream_reply(history: list[dict], message: str) -> Generator[str, None, None]:
    client = _get_client()
    stream = client.models.generate_content_stream(
        model=_get_model(),
        contents=_build_contents(history, message),
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text
