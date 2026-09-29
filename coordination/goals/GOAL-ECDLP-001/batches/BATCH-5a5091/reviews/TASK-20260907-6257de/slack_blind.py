#!/usr/bin/env python3
"""Blind slack re-derivation from archived S2CS fields only.

Must not import or read the S2DX producer or S2DX run artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
S2CS = REPO / "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2CS/raw-result.json"
TARGETS = (
    ("S2-P8219", 9, "floor(Mx/p)"),
    ("S2-P32779", 13, "floor(Mx/p)"),
)


def main() -> int:
    raw = json.loads(S2CS.read_text())
    out = []
    for cell in raw["cells"]:
        cid = cell["id"]
        for ms in cell["Ms"]:
            m = int(ms["M"])
            for arm, rec in ms["arms"].items():
                if (cid, m, arm) not in TARGETS:
                    continue
                aligned = float(rec["cs_bound_recorded"])
                ratio = float(rec["aligned_ratio"])
                out.append(
                    {
                        "cell": cid,
                        "M": m,
                        "arm": arm,
                        "aligned_ratio": ratio,
                        "cs_bound_recorded": aligned,
                        "aligned_holds": bool(rec["aligned_holds"]),
                        "slack": aligned - ratio,
                    }
                )
    if len(out) != 2:
        raise SystemExit(f"expected 2 target rows, got {len(out)}")
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
