import time
import hashlib
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError


def now_ts():
    """Return integer Unix timestamp."""
    return int(time.time())


def hash_payload(model_id: str, index: int, prev_hash: str, payload: str, ts: int) -> str:
    """
    Deterministic hash over all fields except signature.
    """
    h = hashlib.blake2b(digest_size=32)
    h.update(model_id.encode())
    h.update(index.to_bytes(8, "big"))
    h.update(prev_hash.encode())
    h.update(payload.encode())
    h.update(ts.to_bytes(8, "big"))
    return h.hexdigest()


def commit_payload(payload: str) -> str:
    """Commit to the raw payload only."""
    h = hashlib.blake2b(digest_size=32)
    h.update(payload.encode())
    return h.hexdigest()


def generate_keypair():
    """Return (signing_key, verify_key)."""
    sk = SigningKey.generate()
    vk = sk.verify_key
    return sk, vk


def sign_event(message_bytes: bytes, sk: SigningKey) -> bytes:
    """Return signature over message_bytes."""
    return sk.sign(message_bytes).signature


def verify_signature(vk: VerifyKey, message_bytes: bytes, signature: bytes) -> bool:
    """Return True if signature is valid."""
    try:
        vk.verify(message_bytes, signature)
        return True
    except BadSignatureError:
        return False
