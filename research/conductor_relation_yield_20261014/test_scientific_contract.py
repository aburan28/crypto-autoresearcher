"""Custody control: lifecycle approval may not alter scientific terms."""
from __future__ import annotations

from copy import deepcopy

from scientific_contract import SCIENTIFIC_KEYS, digest


def main() -> None:
    draft = {key: {"fixed": key} for key in SCIENTIFIC_KEYS}
    draft["inputs"] = {"primary_pairs": ["P29", "P37"],
                       "implementation": {"trial_plan": "pending"}}
    draft.update(status="review_required", approved_by=None, frozen=False,
                 execution_authorized=False, approval_gate={"missing": ["plan"]})
    approved = deepcopy(draft)
    approved.update(status="approved", approved_by="coordinator", frozen=True,
                    execution_authorized=True, approval_gate={"missing": []})
    approved["inputs"]["implementation"]["trial_plan"] = "trial-plan.json"
    assert digest(draft) == digest(approved)
    changed = deepcopy(approved)
    changed["metrics"]["fixed"] = "different"
    assert digest(draft) != digest(changed)
    changed = deepcopy(approved)
    changed["inputs"]["primary_pairs"].append("P41")
    assert digest(draft) != digest(changed)
    print("scientific-contract digest control: lifecycle stable, metric/input drift rejected PASS")


if __name__ == "__main__":
    main()
