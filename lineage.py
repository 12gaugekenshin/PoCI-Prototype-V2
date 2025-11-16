import sqlite3
from dataclasses import dataclass
from typing import List
import os


GENESIS = "0" * 64
DB_PATH = "events.db"


@dataclass
class Event:
    model_id: str
    index: int
    payload: str
    payload_hash: str
    event_hash: str
    prev_hash: str
    ts: int
    signature: bytes

    def canonical_bytes(self) -> bytes:
        """
        Canonical representation used for signature verification.
        """
        s = f"{self.model_id}|{self.index}|{self.prev_hash}|{self.event_hash}|{self.payload_hash}|{self.ts}"
        return s.encode()

    def commit_to_disk(self):
        """
        Insert event into sqlite table.
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                model_id TEXT,
                index_num INTEGER,
                payload TEXT,
                payload_hash TEXT,
                event_hash TEXT,
                prev_hash TEXT,
                ts INTEGER,
                signature BLOB
            )
            """
        )
        conn.commit()

        cur.execute(
            """
            INSERT INTO events
            (model_id, index_num, payload, payload_hash, event_hash, prev_hash, ts, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.model_id,
                self.index,
                self.payload,
                self.payload_hash,
                self.event_hash,
                self.prev_hash,
                self.ts,
                self.signature,
            ),
        )
        conn.commit()
        conn.close()


class LineageStore:
    """
    Local lineage chain + monotonic index, persisted via sqlite.
    """

    def __init__(self):
        os.makedirs(".", exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                model_id TEXT,
                index_num INTEGER,
                payload TEXT,
                payload_hash TEXT,
                event_hash TEXT,
                prev_hash TEXT,
                ts INTEGER,
                signature BLOB
            )
            """
        )
        conn.commit()
        conn.close()

    def next_index(self) -> int:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT MAX(index_num) FROM events")
        result = cur.fetchone()[0]
        conn.close()
        return 0 if result is None else result + 1

    def last_hash(self, model_id: str) -> str:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT event_hash FROM events WHERE model_id=? ORDER BY index_num DESC LIMIT 1",
            (model_id,),
        )
        row = cur.fetchone()
        conn.close()
        return row[0] if row else GENESIS

    def append(self, event: Event):
        event.commit_to_disk()

    def get_chain(self, model_id: str) -> List[Event]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT model_id, index_num, payload, payload_hash, event_hash, prev_hash, ts, signature
            FROM events
            WHERE model_id=?
            ORDER BY index_num ASC
            """,
            (model_id,),
        )
        rows = cur.fetchall()
        conn.close()

        chain = []
        for row in rows:
            chain.append(
                Event(
                    model_id=row[0],
                    index=row[1],
                    payload=row[2],
                    payload_hash=row[3],
                    event_hash=row[4],
                    prev_hash=row[5],
                    ts=row[6],
                    signature=row[7],
                )
            )
        return chain
