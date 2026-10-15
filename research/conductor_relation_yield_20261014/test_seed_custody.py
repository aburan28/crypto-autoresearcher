"""Static custody checks; deliberately does not draw scientific seeds."""
from __future__ import annotations

import json

from issue_seeds import HERE, SOURCE_NAMES
from reveal_seeds import expected_arms


def main():
    plan = json.loads((HERE / "plan.json").read_text())
    pairs = expected_arms(plan)
    assert len(pairs) == 20
    assert all((endpoint, arm) in pairs for endpoint in ("P29-crater", "P29-floor", "P37-crater", "P37-floor") for arm in ("native", "random", "u2-transport", "u2-native"))
    assert all((endpoint, arm) in pairs for endpoint in ("P29-E2", "P29-E3") for arm in ("native", "random"))
    assert set(SOURCE_NAMES) >= {"plan.json", "issue_seeds.py", "reveal_seeds.py", "execute_prepared.py", "collector.rs", "count_verify.cpp", "verify_collector.py", "exact_interval.py", "prepare_input.py"}
    print("seed custody static control: 20 prespecified arms, frozen-source list, no seed draw PASS")


if __name__ == "__main__":
    main()
