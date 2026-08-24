"""Read configuration from .env files instead of the process environment.

Secrets (MiniMax key etc.) stay in a .env file outside git. Values are read
straight from the file, so the deploy script no longer needs to export them
into Gunicorn's environment, and editing .env takes effect without a restart.

Lookup order (first file that defines a key wins):
  1. path in GABAY_ENV_FILE
  2. <repo>/.env
  3. /home/ubuntu/runtime/.env
  4. /home/ubuntu/runtime/secrets/minimax.env
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_ENV_FILES: tuple[Path, ...] = (
    BASE_DIR / ".env",
    Path("/home/ubuntu/runtime/.env"),
    Path("/home/ubuntu/runtime/secrets/minimax.env"),
)

_cache: dict[str, str] = {}
_cache_stamp: tuple[tuple[str, float], ...] | None = None


def env_files() -> list[Path]:
    files: list[Path] = []
    override = os.environ.get("GABAY_ENV_FILE", "").strip()
    if override:
        files.append(Path(override))
    files.extend(DEFAULT_ENV_FILES)
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in files:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def _stamp(paths: list[Path]) -> tuple[tuple[str, float], ...]:
    marks: list[tuple[str, float]] = []
    for path in paths:
        try:
            marks.append((str(path), path.stat().st_mtime))
        except OSError:
            marks.append((str(path), -1.0))
    return tuple(marks)


def _parse(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return values
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def env_values() -> dict[str, str]:
    """Merged .env contents, refreshed when any source file changes."""
    global _cache, _cache_stamp
    paths = env_files()
    stamp = _stamp(paths)
    if stamp != _cache_stamp:
        merged: dict[str, str] = {}
        for path in paths:
            for key, value in _parse(path).items():
                merged.setdefault(key, value)
        _cache = merged
        _cache_stamp = stamp
    return _cache


def env_value(key: str, default: str = "") -> str:
    return env_values().get(key, default)


def env_source(key: str) -> str:
    """Path of the .env file that supplies a key (for diagnostics)."""
    for path in env_files():
        if key in _parse(path):
            return str(path)
    return ""
