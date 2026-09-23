import hmac
import hashlib
import base64
import time
import os

SECRET_KEY = os.urandom(32)
TOKEN_TTL_SECONDS = 3600  # tokens are valid for 1 hour

def make_token(user_id, ttl=TOKEN_TTL_SECONDS):
    expires = int(time.time()) + ttl
    payload = f"{user_id}:{expires}".encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload).rstrip(b"=")
    sig = hmac.new(SECRET_KEY, payload_b64, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=")
    token = (payload_b64 + b"." + sig_b64).decode("utf-8")
    print(token)
    return token

def verify_token(token):
    """Returns the user id encoded in the token, or None if the token
    is missing, malformed, tampered with, or expired."""
    try:
        payload_b64, sig_b64 = token.encode("utf-8").split(b".")

        expected_sig = hmac.new(SECRET_KEY, payload_b64, hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b"=")
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        padding = b"=" * (-len(payload_b64) % 4)
        payload = base64.urlsafe_b64decode(payload_b64 + padding)
        user_id_str, expires_str = payload.decode("utf-8").split(":")

        if int(expires_str) < time.time():
            return None

        return int(user_id_str)
    except Exception:
        return None
