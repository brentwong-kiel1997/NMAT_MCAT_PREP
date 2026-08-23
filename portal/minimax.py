"""MiniMax M3 client for Gabay study tutor.

API key is loaded from environment or /home/ubuntu/runtime/secrets/minimax.env
and must never be committed to the repository.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


SECRET_FILE = Path("/home/ubuntu/runtime/secrets/minimax.env")


def _load_secret_file() -> None:
    if not SECRET_FILE.exists():
        return
    for raw in SECRET_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_secret_file()


def minimax_config() -> dict[str, str]:
    return {
        "api_key": os.environ.get("MINIMAX_API_KEY", ""),
        "base_url": os.environ.get("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1").rstrip("/"),
        "model": os.environ.get("MINIMAX_MODEL", "MiniMax-M3"),
    }


def chat_completion(
    messages: list[dict],
    *,
    max_tokens: int = 1200,
    temperature: float = 0.4,
) -> str:
    cfg = minimax_config()
    if not cfg["api_key"]:
        raise RuntimeError("MINIMAX_API_KEY is not configured on this server.")

    payload = {
        "model": cfg["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
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
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected MiniMax response: {str(data)[:300]}") from exc

    # MiniMax sometimes wraps thinking tags; strip for learner-facing text.
    if isinstance(content, str) and "</think>" in content:
        content = content.split("</think>", 1)[-1].strip()
    return (content or "").strip()
