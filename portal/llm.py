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
    # the Claude Code CLI style needs no stored key — it reuses the CLI's
    # own configuration, so an empty api_key must not read as "offline"
    return bool(provider and (provider.api_style == "claude-code"
                              or provider.api_key))


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
    provider: AIProvider | None = None,
    timeout: int = 90,
) -> str:
    provider = provider or active_provider()
    if provider is None:
        raise RuntimeError(
            "No AI model is configured. Ask an admin to add one under "
            "Manage → Models."
        )
    if provider.api_style == "claude-code":
        return _call_cc_cli(provider, messages, timeout)
    if not provider.api_key:
        raise RuntimeError(
            f"Provider {provider.name!r} has no API key set. "
            "Update it under Manage → Models."
        )
    base = provider.base_url.rstrip("/")
    if provider.api_style == "anthropic":
        return _call_anthropic(provider, base, messages, max_tokens, temperature,
                               timeout)
    return _call_openai_style(provider, base, messages, max_tokens, temperature,
                              timeout)


def _run_cc_cli(args: list[str], stdin_text: str, timeout: int, cwd: str):
    """Invoke the claude CLI. Factored out so tests can patch the runner."""
    import subprocess

    return subprocess.run(
        ["claude", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# The study coach never needs tools; denying the full set keeps a crafted
# learner prompt from driving Bash/Write even though this machine's user
# settings carry bypassPermissions (verified: tools stay unavailable under
# --disallowedTools regardless of that setting).
_CC_DENIED_TOOLS = ("Bash BashOutput KillShell Write Edit NotebookEdit "
                    "WebFetch WebSearch Task TodoWrite TodoRead Read Grep Glob")


def _call_cc_cli(provider, messages: list[dict], timeout: int) -> str:
    """Study-coach completion through the local Claude Code CLI.

    Reuses the server's existing CC model configuration (auth + routing)
    while staying isolated from any interactive/development CC sessions:
    every call is stateless (-p, fresh session id, never --continue or
    --resume), runs with cwd inside a dedicated empty workspace (REQUIRED —
    inheriting the deploy checkout would load its project config and write
    session transcripts into its project space), denies all tools, and
    forces the manual permission mode as a second lock against the
    user-level bypassPermissions setting.

    Note: max_tokens/temperature have no CLI equivalents — replies are
    bounded only by the CLI itself; the shared daily budget caps total use.
    """
    import json as _json
    import os

    from django.conf import settings

    workspace = getattr(settings, "CC_WORKSPACE", "")
    if not workspace:
        raise RuntimeError("CC_WORKSPACE is not configured")
    os.makedirs(workspace, exist_ok=True)

    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    convo = "\n\n".join(
        f"{m['role'].upper()}: {m['content']}" if m["role"] != "system" else ""
        for m in messages
    ).strip()

    args = [
        "-p", "--output-format", "json",
        "--permission-mode", "manual",
        "--disallowedTools", _CC_DENIED_TOOLS,
    ]
    if system:
        args += ["--system-prompt", system[:4000]]
    if provider.model_id:
        args += ["--model", provider.model_id]

    try:
        proc = _run_cc_cli(args, convo, timeout=timeout, cwd=workspace)
    except Exception as exc:  # timeout / binary missing
        raise RuntimeError(f"claude CLI call failed: {exc}") from exc
    finally:
        _sweep_cc_transcripts(workspace)
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited {proc.returncode}: {proc.stderr[:300]}")
    try:
        data = _json.loads(proc.stdout)
    except _json.JSONDecodeError as exc:
        raise RuntimeError(
            f"claude CLI returned non-JSON: {proc.stdout[:200]}") from exc
    if data.get("is_error"):
        raise RuntimeError(f"claude CLI error: {str(data.get('result'))[:300]}")
    text = data.get("result") or ""
    cleaned = _clean(text)
    return cleaned or "(the model returned no visible text — please try again)"


def _sweep_cc_transcripts(workspace: str) -> None:
    """Best-effort hygiene: -p calls still write session transcripts under
    ~/.claude/projects/<workspace-slug>/. Drop files older than a day so
    learner prompt content (and disk) does not accumulate forever."""
    import os
    import time

    home = os.path.expanduser("~")
    slug = workspace.strip("/").replace("/", "-")
    proj = os.path.join(home, ".claude", "projects", slug)
    try:
        cutoff = time.time() - 24 * 3600
        for name in os.listdir(proj):
            path = os.path.join(proj, name)
            try:
                if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                    os.unlink(path)
            except OSError:
                pass
    except OSError:
        pass


def _post(url: str, headers: dict, payload: dict, timeout: int = 90):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"{url} HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{url} network error: {exc}") from exc


def _call_openai_style(
    provider, base: str, messages: list[dict], max_tokens: int, temperature: float,
    timeout: int = 90,
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
        timeout,
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
    provider, base: str, messages: list[dict], max_tokens: int, temperature: float,
    timeout: int = 90,
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
        timeout,
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
