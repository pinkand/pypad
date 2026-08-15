"""
Lightweight auth utilities using only the standard library.
- Password hashing: PBKDF2-HMAC-SHA256 (stdlib hashlib)
- JWT: HMAC-SHA256 signed tokens (no external deps)
"""
import hashlib
import hmac
import json
import base64
import secrets
import time
from typing import Optional, Dict

# Secret key for JWT signing — in production, load from env
JWT_SECRET = secrets.token_hex(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days


def hash_password(password: str) -> str:
    """Hash a password with a random salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a PBKDF2-HMAC-SHA256 hash."""
    try:
        salt, dk_hex = hashed.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def create_token(payload: Dict) -> str:
    """Create a JWT-like token signed with HMAC-SHA256."""
    header = _b64_encode(json.dumps({"alg": JWT_ALGORITHM, "typ": "JWT"}).encode())
    body = {**payload, "exp": int(time.time()) + JWT_EXPIRE_SECONDS, "iat": int(time.time())}
    body_b64 = _b64_encode(json.dumps(body).encode())
    sig_input = f"{header}.{body_b64}".encode()
    signature = _b64_encode(hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest())
    return f"{header}.{body_b64}.{signature}"


def decode_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT-like token. Returns payload or None if invalid."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, body_b64, signature = parts
        # Verify signature
        sig_input = f"{header}.{body_b64}".encode()
        expected = _b64_encode(hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(_b64_decode(body_b64))
        # Check expiry
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
