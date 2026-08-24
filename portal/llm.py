"""Chat-completion client for the study coach, with swappable providers.

The active provider is a row in the AIProvider table (managed by staff in
the admin UI — add, delete, pick). Two wire protocols are supported:

  openai    POST {base_url}/chat/completions   (OpenAI, MiniMax, most proxies)
  anthropic POST {base_url}/v1/messages        (Anthropic Messages API)

Credentials live server-side only (DB row), never in the repository.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from .models import AIProvider

# Reasoning models can wrap private thinking in <think>...</think>; the study
# UI needs the visible answer only.
_THINK_RE = re.compile(r"<think>[\s\S]*?</think>", re.IGNORECASE)


def active_provider() -> AIProvider | None:
    return AIProvider.objects.filter(is_active=True).first()


def coach_label() -> str:
    provider = active_provider()
    return f"{provider.name} · {provider.model_id}" if provider else ""


def coach_ready() -> bool:
    provider = active_provider()
    return bool(provider and provider.api_key)


def coach_context(request) -> dict:
    """Template context: current coach model for every page."""
    return {"coach_label": coach_label(), "coach_ready": coach_ready()}


def _clean(content: str) -> str:
    return _THINK_RE.sub("", content or "").strip()


def chat_completion(
    messages: list[dict],
    *,
    max_tokens: int = 1200,
    temperature: float = 0.4,
) -> str:
    provider = active_provider()
    if provider is None:
        raise RuntimeError(
            "No AI model is configured. Ask an admin to add one under "
            "Manage → Models."
        )
    if not provider.api_key:
        raise RuntimeError(
            f"Provider {provider.name!r} has no API key set. "
            "Update it under Manage → Models."
        )
    base = provider.base_url.rstrip("/")
    if provider.api_style == "anthropic":
        return _call_anthropic(provider, base, messages, max_tokens, temperature)
    return _call_openai_style(provider, base, messages, max_tokens, temperature)


def _post(url: str, headers: dict, payload: dict):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"{url} HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{url} network error: {exc}") from exc


def _call_openai_style(
    provider, base: str, messages: list[dict], max_tokens: int, temperature: float
) -> str:
    payload: dict = {
        "model": provider.model_id,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # thinking-budget control is MiniMax-specific; other OpenAI-compatible
    # servers reject unknown top-level params, so scope it to MiniMax hosts.
    if "minimax" in base:
        payload["thinking"] = {"type": "disabled"}
    data = _post(
        f"{base}/chat/completions",
        {"Authorization": f"Bearer {provider.api_key}"},
        payload,
    )
    try:
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected response: {str(data)[:300]}") from exc
    cleaned = _clean(content if isinstance(content, str) else str(content))
    if cleaned:
        return cleaned
    reasoning = message.get("reasoning") if isinstance(message, dict) else None
    if reasoning:
        cleaned_r = _clean(str(reasoning))
        if cleaned_r:
            return cleaned_r
    return "(the model returned no visible text — please try again)"


def _call_anthropic(
    provider, base: str, messages: list[dict], max_tokens: int, temperature: float
) -> str:
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    convo = [m for m in messages if m["role"] != "system"]
    payload: dict = {
        "model": provider.model_id,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": convo,
    }
    if system:
        payload["system"] = system
    data = _post(
        f"{base}/v1/messages",
        {
            "x-api-key": provider.api_key,
            "anthropic-version": "2023-06-01",
        },
        payload,
    )
    try:
        parts = [
            block.get("text", "")
            for block in data["content"]
            if block.get("type") == "text"
        ]
    except (KeyError, TypeError) as exc:
        raise RuntimeError(f"Unexpected response: {str(data)[:300]}") from exc
    cleaned = _clean("\n".join(parts))
    return cleaned or "(the model returned no visible text — please try again)"
