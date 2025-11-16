Proof-Of-Compute-Integrity Prototype
---
You must READ the HOW TO RUN PROTOTYPE for this branch in order to run this prototype!

Fixes Include from V1: 

1. Payload Commitment Added
Raw payload now gets its own BLAKE2b commitment (payload_commit)
Prevents models from lying about inputs/outputs

2. Canonical Serialization for Signatures
All signature verification now uses a single canonical byte format
Eliminates ambiguity and fragile hand-built message reconstruction.

3. SQLite Persistence (Full Lineage Database)
Events are now written to disk (poc_integrity.db)
Provenance survives restarts
Enables deterministic replay and offline verification

4. Global Monotonic Event Index
Every event across all models shares a single increasing index
Prevents index collisions and ensures global ordering

5. Per-Model Monotonic Timestamp Enforcement
Each model’s timestamps can only move forward
Blocks replay/time-drift manipulation

6. Fixed-Point Trust Weights (No Floats)
weight stored as 0–1000
theta stored as 50–500
Makes controller deterministic and consensus-safe

7. Unified Event Hash Logic
payload_hash and event_hash unified
No double hashing or mismatch conditions

8. DB-Driven Last Hash & Last Timestamp State
Restart automatically reloads last hash + timestamp per model
Preserves lineage continuity across sessions

9. Deterministic Replay of Entire Event History
System can reload from SQLite and recompute trust curves exactly
Confirms reproducibility and correctness of the PoCI loop
