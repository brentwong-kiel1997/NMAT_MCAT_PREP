"""Tiny time-window hit counters for self-serve endpoints.

Process-level counters (a module dict), NOT the Django cache: request_finished
closes cache connections, and LocMemCache.close() empties the store — a
cache-backed counter silently resets on every request. With gunicorn
workers=2 each worker counts independently, so real limits are up to 2× the
configured number; that is fine for stopping runaway farming/DoS. Login
lockouts use django-axes instead (DB-backed, cross-worker).
"""

from __future__ import annotations

import time

_hits: dict[str, list[float]] = {}


def hit(key: str, limit: int, window_seconds: int) -> bool:
    """Record one hit under `key`; True while under `limit`."""
    now = time.monotonic()
    bucket = [t for t in _hits.get(key, ()) if now - t < window_seconds]
    if len(bucket) >= limit:
        _hits[key] = bucket
        return False
    bucket.append(now)
    _hits[key] = bucket
    if len(_hits) > 10_000:  # defensive: drop exhausted keys wholesale
        for k in [k for k, v in _hits.items() if not v]:
            del _hits[k]
    return True


def reset() -> None:
    """Test helper: clear all counters."""
    _hits.clear()


def client_ip(request) -> str:
    """Best-effort client IP. X-Real-IP is set (overwritten) by our nginx,
    so it is trustworthy there; plain deployments fall back to REMOTE_ADDR."""
    return (request.META.get("HTTP_X_REAL_IP")
            or request.META.get("REMOTE_ADDR")
            or "unknown")
