#!/usr/bin/env python3
"""Write impl/impl-provenance.json (C-PROV): for every file of this impl/, the
Stage-1 source path and sha256 (experiments/EXP-CERTBIN-4e92d7/impl/, reviewed
in REVIEW-CERTBIN-20260923-c51f07), the new sha256, the unified diff and the
reason for each change. NEW files have no source.

  python3 experiments/EXP-CERTBIN-3f06d1/impl/make_provenance.py
"""
import difflib
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "experiments", "EXP-CERTBIN-4e92d7", "impl")
OUT = os.path.join(HERE, "impl-provenance.json")

REASONS = {
    "gf2n.py": "unchanged",
    "curve.py": "unchanged",
    "elim.py": "unchanged",
    "stats.py": "unchanged (descriptive helpers only: entropy, median, Mann-Whitney; every interval and tail now comes from xstats.py)",
    "macaulay.py": "object.unknowns: the descent takes the cell's V basis b_0..b_8 (x_1 = sum v_j b_j, x_2 = sum v_{9+j} b_j); the default is the Stage-1 polynomial basis, so the Stage-1 output is unchanged (checked by C-PROV).",
    "oracles.py": "object.unknowns / EX-3: oracle A enumerates x_1 = comb(u_1) over the cell's basis and keeps a root iff the linear-algebra membership test V.coord succeeds; witness verification and the rational flag map u to x_i through the basis.",
    "families.py": "v2 cells: R1/R2 curve draws with a required cofactor (R2 excludes the Stage-1 curve), R3 reads the archived Stage-1 curve (sha256-checked), the R3 random V (S_V), degenerate stratum by V-membership, one affine null draw (F-AFF-1), per-cell C-SELF items and C-TR before any reference/target stream, x(2E) class per instance, F-RANDX / F-S3 shared-x_R listing, the F-NULLF2 union-support positions for C-NULLS.",
    "engine.py": "C-REV needs a pivot-column-set hash per instance; C-AFF 'every reference' needs the reference's direct self-replay compared with its forms at r_ref; C-FORMS needs a second (scalar) forms-evaluation path and the direct-replay first-zero comparison; hull accounting needs the linear parts a_k in every hazard table; C-NULLS needs the code-path sha256 per unit; targets carry their x(2E) class.",
    "selftest.py": "S_selftest = 2026092410099; C-SELF extended: random-V descent, Macaulay rows and oracle cross-checks, V-membership vs brute force, the [#E/2] x(2E) test vs a brute-force halving search; the per-cell items (cell_selftest) run in phase 1 on each cell's curve and V.",
    "driver.py": "three cells (R1, R2, R3) with per-cell checkpoints; --stage1-run; C-PROV and selftest gate phase 1; phase 7 (C-DET) on the references and the 200 lowest-idx F-S3 targets per cell; phase 8 extracts PS0' certificates (row-combination tracker) and writes cells.json; phase 9 after the separate-process verifier.",
    "analysis.py": "rewritten for the v2 metrics: M1 with exact CP, M1f, M1k (hull accounting, Sigma, Sigma_H), M2R / TS1R with RC-2 deduplication and exact bands and tail, M-R4 with the x(2E) split and the exact Fisher test, M3 with the F-J3-1 precedence, M4, the v2 controls (C-FORMS, C-SURV, C-HZERO, C-TR, C-REV, C-NULLS, PS0'), INV-1..INV-7 and RR-1..RR-10.",
    "report.py": "rewritten for the v2 artifacts (per-cell references, targets and pivot-hazards files, cells.json, certificates), the independent raw-result recomputation (own hull, restriction, band and median code) and the v2 manifest.",
    "make_trial_plan.py": "rewritten for the v2 plan: per-cell seed table, v2 counts, interpretations I-1..I-40.",
    "README.md": "rewritten for this experiment.",
    "vspace.py": "NEW: the V basis (comb, linear-algebra membership), the S_V draw, and small F_2 linear algebra on 17-bit ints (echelon, affine hull, restriction, affine systems).",
    "x2e.py": "NEW: the [#E/2] x(2E) test, the per-x enumeration, the brute-force doubling image and C-TR.",
    "xstats.py": "NEW (RC-3): exact binomial bands and tails, exact one-sided Fisher test, Clopper-Pearson by bisection in 80-digit decimal arithmetic.",
    "cprov.py": "NEW: C-PROV (the replication code on the Stage-1 cell against the archived values).",
    "make_provenance.py": "NEW: writes this file.",
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    files = sorted(f for f in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, f))
                   and f != "impl-provenance.json" and not f.endswith(".pyc"))
    out = {"source_impl": "experiments/EXP-CERTBIN-4e92d7/impl/", "source_review": "REVIEW-CERTBIN-20260923-c51f07",
           "rule": "copied, never imported or edited in place; every change listed here (EX-1, C-PROV)", "files": {}}
    missing_reason = []
    for f in files:
        new = open(os.path.join(HERE, f), "rb").read()
        src_p = os.path.join(SRC, f)
        e = {"sha256": sha(new), "reason": REASONS.get(f)}
        if e["reason"] is None:
            missing_reason.append(f)
        if os.path.exists(src_p):
            old = open(src_p, "rb").read()
            e["source"] = f"experiments/EXP-CERTBIN-4e92d7/impl/{f}"
            e["source_sha256"] = sha(old)
            e["changed"] = old != new
            e["unified_diff"] = "".join(difflib.unified_diff(
                old.decode().splitlines(keepends=True), new.decode().splitlines(keepends=True),
                fromfile=f"EXP-CERTBIN-4e92d7/impl/{f}", tofile=f"EXP-CERTBIN-3f06d1/impl/{f}")) if old != new else ""
        else:
            e["source"] = None
            e["new_file"] = True
        out["files"][f] = e
    dropped = sorted(set(os.listdir(SRC)) - set(files))
    out["source_files_not_copied"] = dropped
    if missing_reason:
        print(f"no reason recorded for {missing_reason}", file=sys.stderr)
        return 1
    if os.path.exists(OUT):
        os.remove(OUT)  # regenerated from the current tree before C-PROV; never after it
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
