# models.py
from crypto_utils import (
    generate_keypair,
    commit_payload,
    hash_payload,
    now_ts,
    sign_event,
)
from lineage import Event


class BaseModel:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.sk, self.vk = generate_keypair()
        self.last_ts = 0

    def make_event(self, store, payload: str, cheat=False) -> Event:
        # Monotonic global index from lineage store
        idx = store.next_index()

        # Last event hash for this model
        prev_hash = store.last_hash(self.model_id)

        # Monotonic timestamp
        ts = now_ts()
        if ts <= self.last_ts:
            ts = self.last_ts + 1
        self.last_ts = ts

        # Payload commit (hash of actual data)
        payload_commit = commit_payload(payload)

        # Event hash (canonical structural hash)
        ev_hash = hash_payload(self.model_id, idx, prev_hash, payload, ts)

        # Canonical message to sign  (MUST MATCH Event.canonical_bytes)
        canonical = (
            f"{self.model_id}|{idx}|{prev_hash}|{ev_hash}|{payload_commit}|{ts}"
        ).encode()

        # Cheat mode = reverse bytes to force invalid signature
        message_bytes = canonical if not cheat else canonical[::-1]

        # Signature using Ed25519 keypair
        sig = sign_event(message_bytes, self.sk)

        # Return event object (payload_hash MUST be payload_commit)
        return Event(
            model_id=self.model_id,
            index=idx,
            payload=payload,
            payload_hash=payload_commit,   # ✔ FIXED!
            event_hash=ev_hash,
            prev_hash=prev_hash,
            ts=ts,
            signature=sig,
        )


class HonestModel(BaseModel):
    pass


class AttackerModel(BaseModel):
    pass
