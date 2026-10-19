"""Orchestration layer: inference policy, backend bindings, and the adapter.

Role contracts live in `agents/`; this package owns only the question of which
inference endpoint serves a role, and records the answer so a run manifest can
be audited later.
"""
