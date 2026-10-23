"""Render recorded P29-E2/E3 native yields from EXP-ECTD-0cf008."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUNS = ROOT / "experiments/EXP-ECTD-0cf008/runs"
OUT = Path(__file__).with_name("yield.svg")
ARMS = (
    ("P29-E2-native", "RUN-ECTD-c769f1"),
    ("P29-E3-native", "RUN-ECTD-f395a9"),
)


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    rows = []
    for label, run_id in ARMS:
        result = json.loads((RUNS / run_id / "raw-result.json").read_text())
        verified = result["verified"]
        interval = result["interval"]
        receipt = json.loads((RUNS / run_id / "execution-receipt.json").read_text())
        if (receipt.get("status") != "output_validated" or
                result.get("status") != "completed_unreviewed" or
                verified.get("status") != "valid" or
                verified.get("targets") != 32768 or
                verified.get("independent_ordered_count_match") is not True):
            raise ValueError(f"{run_id}: source run is not an output-validated native arm")
        rows.append({"label": label, "run_id": run_id,
                     "n": verified["targets"], "successes": verified["useful_targets"],
                     "fraction": interval["observed"] / interval["draws"],
                     "lower": interval["lower_fraction"],
                     "upper": interval["upper_fraction"]})

    width, height = 960, 500
    left, right, top, bottom = 100, 900, 48, 345
    ymax = 0.08
    y = lambda value: bottom - value / ymax * (bottom - top)
    x_positions = (320, 680)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<text x="480" y="25" text-anchor="middle" font-family="Helvetica,Arial" font-size="18" font-weight="bold">P29 same-conductor native useful-target fractions</text>']
    for tick in range(0, 9):
        value = tick / 100
        yy = y(value)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#d8dee8"/>')
        parts.append(f'<text x="{left-12}" y="{yy+5:.1f}" text-anchor="end" font-family="Helvetica,Arial" font-size="13">{value:.2f}</text>')
    parts += [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#263746"/>',
              f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#263746"/>',
              f'<text x="24" y="{(top+bottom)//2}" transform="rotate(-90 24 {(top+bottom)//2})" text-anchor="middle" font-family="Helvetica,Arial" font-size="14">Useful targets / attempted targets</text>']
    for x, row in zip(x_positions, rows):
        ylow, yhigh, yobs = y(row["lower"]), y(row["upper"]), y(row["fraction"])
        parts += [f'<line x1="{x}" y1="{yhigh:.1f}" x2="{x}" y2="{ylow:.1f}" stroke="#c66b22" stroke-width="3"/>',
                  f'<line x1="{x-12}" y1="{yhigh:.1f}" x2="{x+12}" y2="{yhigh:.1f}" stroke="#c66b22" stroke-width="3"/>',
                  f'<line x1="{x-12}" y1="{ylow:.1f}" x2="{x+12}" y2="{ylow:.1f}" stroke="#c66b22" stroke-width="3"/>',
                  f'<circle cx="{x}" cy="{yobs:.1f}" r="7" fill="#235d91"/>',
                  f'<text x="{x}" y="{bottom+27}" text-anchor="middle" font-family="Helvetica,Arial" font-size="15">{esc(row["label"])}</text>',
                  f'<text x="{x}" y="{bottom+49}" text-anchor="middle" font-family="Helvetica,Arial" font-size="13">{row["successes"]}/{row["n"]} = {row["fraction"]:.6f}</text>',
                  f'<text x="{x}" y="{yhigh-10:.1f}" text-anchor="middle" font-family="Helvetica,Arial" font-size="12">99.75% exact interval</text>',
                  f'<text x="{x}" y="{bottom+82}" text-anchor="middle" font-family="Helvetica,Arial" font-size="12">{row["run_id"]}</text>']
    parts += ['<text x="500" y="465" text-anchor="middle" font-family="Helvetica,Arial" font-size="12">Intervals copied from the recorded exact hypergeometric results; native arms only. Source experiment remains incomplete.</text>', '</svg>']
    OUT.write_text("\n".join(parts) + "\n")
    print(json.dumps({"schema": "ectd.prior-same-conductor-plot.v1",
                      "source_runs": [row["run_id"] for row in rows],
                      "output": str(OUT), "status": "rendered"}, sort_keys=True))


if __name__ == "__main__":
    main()
