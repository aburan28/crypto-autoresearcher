"""Derive exact fixed-bound and within-field summaries from the sealed run."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/exact-20261023T1811Z"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    dest = HERE / "analysis.json"
    if dest.exists():
        raise ValueError("refuse analysis overwrite")
    data = json.loads((RUN / "exact/results.json").read_text())
    verified = json.loads((RUN / "verification.json").read_text())
    if sha(RUN / "exact/results.json") != verified["results_sha256"] or len(verified["rows"]) != 19:
        raise ValueError("verification binding failure")
    rows = data["rows"]
    bounds = (100, 1000, 10000, 1000000)
    within = {}
    for field in sorted({r["field_bits"] for r in rows}):
        omitted = [r for r in rows if r["field_bits"] == field and r["label"] == "omitted"]
        published = [r for r in rows if r["field_bits"] == field and r["label"] == "published"]
        pairings = [(int(o["k"]), int(p["k"])) for o in omitted for p in published]
        within[str(field)] = {"omitted": len(omitted), "published": len(published),
                              "pair_count": len(pairings),
                              "omitted_k_less": sum(o < p for o, p in pairings),
                              "omitted_k_equal": sum(o == p for o, p in pairings),
                              "omitted_k_greater": sum(o > p for o, p in pairings)}
    output = {"exact_run_results_sha256": verified["results_sha256"],
              "exact_run_verification_sha256": sha(RUN / "verification.json"),
              "rows": len(rows), "omitted": sum(r["label"] == "omitted" for r in rows),
              "published": sum(r["label"] == "published" for r in rows),
              "minimum_k_bits_all": min(r["k_bits"] for r in rows),
              "minimum_k_bits_omitted": min(r["k_bits"] for r in rows if r["label"] == "omitted"),
              "counts_at_or_below_fixed_bounds": {str(B): sum(int(r["k"]) <= B for r in rows) for B in bounds},
              "within_field_pairs": within}
    dest.write_text(json.dumps(output, indent=2) + "\n")
    print(dest)


if __name__ == "__main__":
    main()
