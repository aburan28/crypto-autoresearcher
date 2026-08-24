"""Stage live-set tracker for FC0-EXT-PKG-SSI-001 scaffolding.

Tracks membership against the frozen stage_live_sets checklist. Does not
compute peak memory widths or convert retries into peak bounds.
"""

from __future__ import annotations

from typing import Dict, Set

from .types import OpaqueHandle


STAGE_LIVE_SETS: Dict[str, Set[str]] = {
    "preparation": {"B_input", "B_attempt", "W_label", "R_label"},
    "sieve_attempt": {"B_input", "B_attempt", "W_sieve", "R_sieve", "B_sieve"},
    "recovery": {
        "B_input",
        "B_attempt",
        "B_post",
        "B_recovery",
        "accepted_transcript",
    },
    "tail_verification": {
        "B_input",
        "B_attempt",
        "B_recovery",
        "M_tail",
        "B_candidate",
    },
}


class StageLiveSetTracker:
    """Checklist tracker for which object ids are currently live."""

    def __init__(self) -> None:
        self.live: Set[str] = set()
        self.history: list[dict] = []

    def birth(self, object_id: str, stage: str) -> None:
        self.live.add(object_id)
        self.history.append({"event": "birth", "object_id": object_id, "stage": stage})

    def destroy(self, object_id: str) -> None:
        self.live.discard(object_id)
        self.history.append({"event": "destroy", "object_id": object_id})

    def live_subset_of_stage(self, stage: str) -> bool:
        allowed = STAGE_LIVE_SETS[stage]
        return self.live.issubset(allowed)

    def required_members_present(self, stage: str, required: Set[str]) -> bool:
        return required.issubset(self.live)

    def peak_accounting_note(self) -> str:
        return (
            "Required peak is max over named stage live sets, not a sum. "
            "This scaffold supplies no numeric widths; peak bound unresolved."
        )

    def snapshot(self) -> dict:
        return {
            "live": sorted(self.live),
            "history_len": len(self.history),
            "peak_accounting_note": self.peak_accounting_note(),
        }


def assert_handle_live(handle: OpaqueHandle) -> None:
    from .types import HandleState

    if handle.state not in (HandleState.live, HandleState.last_used):
        raise RuntimeError(f"handle_{handle.object_id}_not_live:{handle.state.value}")
