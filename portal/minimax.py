"""MiniMax M3 client for Gabay study tutor.

Credentials come from a .env file (see portal/envfile.py); they are never read
from the process environment and never committed to the repository.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from .envfile import env_value


# MiniMax M3 often wraps private reasoning in <think>...</think>
_THINK_RE = re.compile(r"<think>[\s\S]*?</think>", re.IGNORECASE)


def minimax_config() -> dict[str, str]:
    return {
        "api_key": env_value("MINIMAX_API_KEY"),
        "base_url": env_value("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1").rstrip("/"),
        "model": env_value("MINIMAX_MODEL", "MiniMax-M3"),
    }


def _clean_content(content: str) -> str:
    text = _THINK_RE.sub("", content or "")
    return text.strip()


def chat_completion(
    messages: list[dict],
    *,
    max_tokens: int = 1200,
    temperature: float = 0.4,
) -> str:
    cfg = minimax_config()
    if not cfg["api_key"]:
        raise RuntimeError("MINIMAX_API_KEY is missing from the .env file on this server.")

    payload = {
        "model": cfg["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        # Study UI needs visible answers; M3 thinking can consume the whole budget.
        "thinking": {"type": "disabled"},
    }
    req = urllib.request.Request(
        f"{cfg['base_url']}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"MiniMax HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"MiniMax network error: {exc}") from exc

    try:
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected MiniMax response: {str(data)[:300]}") from exc

    cleaned = _clean_content(content if isinstance(content, str) else str(content))
    if cleaned:
        return cleaned
    reasoning = message.get("reasoning") if isinstance(message, dict) else None
    if reasoning:
        cleaned_r = _clean_content(str(reasoning))
        if cleaned_r:
            return cleaned_r
    return "(the model returned no visible text — please try again)"
