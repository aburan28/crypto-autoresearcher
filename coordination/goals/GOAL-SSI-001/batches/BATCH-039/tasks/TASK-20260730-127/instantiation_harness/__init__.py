"""BATCH-039 gate-A protocol-toy peak-byte instantiation harness (zero compute).

Recomputes every protocol-derived numeric in ``instantiation_ledger.yaml`` from
the declared constants in ``protocol_spec.md`` (FC0-PEAKBYTE-TOY-PROTOCOL-R1)
over the BATCH-023 stage membership, and fails on invented / out-of-protocol
numerics or illicit clearance flags. Protocol-toy / scaffold-scale only; not a
QUERY_MEMORY clearance and not a cryptographic-scale bound.
"""
