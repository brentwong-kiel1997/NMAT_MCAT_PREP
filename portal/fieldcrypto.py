"""Encryption at rest for secret model fields (AI provider API keys).

Keys are Fernet-encrypted with a key derived from Django's SECRET_KEY, so no
second secret has to be provisioned. Legacy rows that still hold plaintext
decrypt as-is and are re-encrypted the next time the field is saved.
"""

from __future__ import annotations

import base64
import hashlib

from django.conf import settings

_FERNET_PREFIX = "gAAAA"  # Fernet tokens always start with the version byte '0x80' b64-encoded

_cipher = None
_tried = False


def _get_cipher():
    global _cipher, _tried
    if not _tried:
        _tried = True
        try:
            from cryptography.fernet import Fernet

            digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
            _cipher = Fernet(base64.urlsafe_b64encode(digest))
        except ImportError:
            _cipher = None  # degrade to plaintext store rather than break the app
    return _cipher


def encrypt_value(raw: str) -> str:
    """Encrypt; returns the ciphertext token (or the input if crypto is unavailable)."""
    raw = raw or ""
    cipher = _get_cipher()
    if not cipher or not raw or raw.startswith(_FERNET_PREFIX):
        return raw
    return cipher.encrypt(raw.encode("utf-8")).decode("ascii")


def decrypt_value(raw: str) -> str:
    """Decrypt a stored value; plaintext legacy values pass through unchanged."""
    raw = raw or ""
    if not raw.startswith(_FERNET_PREFIX):
        return raw
    cipher = _get_cipher()
    if not cipher:
        return ""
    try:
        return cipher.decrypt(raw.encode("ascii")).decode("utf-8")
    except Exception:
        return ""  # wrong key / corrupt token — behave like an unset key
