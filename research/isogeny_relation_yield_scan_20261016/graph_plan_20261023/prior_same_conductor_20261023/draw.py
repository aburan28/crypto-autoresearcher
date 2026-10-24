"""Render recorded P29-E2/E3 native yields from EXP-ECTD-0cf008."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUNS = ROOT / "experiments/EXP-ECTD-0cf008/runs"
OUT = Path(__file__).with_name("yield.svg")
ARMS = (
    ("P29-E2-native", "RUN-ECTD-c769f1"),
    ("P29-E3-native", "RUN-ECTD-f395a9"),
)
PREPARED = Path("experiments/EXP-ECTD-0cf008/preparation/prepared")
COEFFICIENT_STREAMS = {
    "P29-floor": "64cd3756f380960a5a574e78f3d4a274f45dd70e841d31691a03bbbe588c51ca",
    "P29-E2": "80d447c67d0d403e58614bdcef54cd260cab2ea3500be509c1982bf0cd3cb3c5",
    "P29-E3": "2917b209cce21d597c9b1ecded06a4c9d484ca28d979a0efb65bf37bbe0fc7a3",
}
LEGACY_PREPARER = ROOT / "research/conductor_relation_yield_20261014/prepare_input.py"
LEGACY_PREPARER_SHA256 = "7bec20e2147641539d8dfdcc0ae0009581e485462396897f0751c879e4b32fef"
CURVE_IDENTITIES = {
    "P29-floor": (320092037, 101186781, 57596093, 320091991, [0, 112219098]),
    "P29-E2": (320092037, 64570613, 54195252, 320091991, [0, 5368294]),
    "P29-E3": (320092037, 234001141, 79995391, 320091991, [5, 53527325]),
}


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def coefficient_stream(endpoint: str) -> tuple[str, list[tuple[int, int]]]:
    path = ROOT / PREPARED / endpoint / "native/prepared.txt"
    manifest = json.loads(path.with_name("manifest.json").read_text())
    input_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected_identity = CURVE_IDENTITIES[endpoint]
    if (input_digest != manifest.get("input_sha256") or
            manifest.get("target_count") != 32768 or
            manifest.get("generator") != expected_identity[4]):
        raise ValueError(f"{endpoint}: prepared manifest does not bind the input and identity")
    digest = hashlib.sha256()
    first: list[tuple[int, int]] = []
    with path.open(encoding="utf-8") as stream:
        header = stream.readline().split()
        if len(header) != 7 or header[0] != "curve":
            raise ValueError(f"{endpoint}: invalid prepared-input header")
        identity = tuple(int(value) for value in header[1:5])
        if identity != expected_identity[:4]:
            raise ValueError(f"{endpoint}: prepared curve identity differs")
        base_count, target_count = int(header[5]), int(header[6])
        for _ in range(base_count):
            if not stream.readline().startswith("base "):
                raise ValueError(f"{endpoint}: missing prepared base row")
        for index in range(target_count):
            fields = stream.readline().split()
            if len(fields) != 6 or fields[:2] != ["target", str(index)]:
                raise ValueError(f"{endpoint}: malformed target coefficient row {index}")
            alpha, beta = int(fields[2]), int(fields[3])
            digest.update(f"{alpha} {beta}\n".encode())
            if index < 3:
                first.append((alpha, beta))
        if stream.readline():
            raise ValueError(f"{endpoint}: prepared input has trailing rows")
    value = digest.hexdigest()
    if value != COEFFICIENT_STREAMS[endpoint]:
        raise ValueError(f"{endpoint}: coefficient-stream digest differs")
    return value, first


def main() -> None:
    if hashlib.sha256(LEGACY_PREPARER.read_bytes()).hexdigest() != LEGACY_PREPARER_SHA256:
        raise ValueError("archived legacy preparer source differs from the recorded run version")
    rows = []
    for label, run_id in ARMS:
        result = json.loads((RUNS / run_id / "raw-result.json").read_text())
        verified = result["verified"]
        interval = result["interval"]
        receipt = json.loads((RUNS / run_id / "execution-receipt.json").read_text())
        environment = json.loads((RUNS / run_id / "environment.json").read_text())
        if (receipt.get("status") != "output_validated" or
                result.get("status") != "completed_unreviewed" or
                verified.get("status") != "valid" or
                verified.get("targets") != 32768 or
                verified.get("independent_ordered_count_match") is not True or
                environment.get("source_sha256", {}).get(
                    "research/conductor_relation_yield_20261014/prepare_input.py") != LEGACY_PREPARER_SHA256):
            raise ValueError(f"{run_id}: source run is not an output-validated native arm")
        rows.append({"label": label, "run_id": run_id,
                     "n": verified["targets"], "successes": verified["useful_targets"],
                     "fraction": interval["observed"] / interval["draws"],
                     "lower": interval["lower_fraction"],
                     "upper": interval["upper_fraction"]})

    coefficient_audit = {}
    for endpoint in COEFFICIENT_STREAMS:
        digest, first = coefficient_stream(endpoint)
        coefficient_audit[endpoint] = {"sha256": digest, "first_three": first}
    if len({row["sha256"] for row in coefficient_audit.values()}) != 3:
        raise ValueError("archived E1/E2/E3 coefficient streams unexpectedly match")

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
                      "legacy_preparer_sha256": LEGACY_PREPARER_SHA256,
                      "coefficient_streams": coefficient_audit,
                      "output": str(OUT), "status": "rendered"}, sort_keys=True))


if __name__ == "__main__":
    main()
