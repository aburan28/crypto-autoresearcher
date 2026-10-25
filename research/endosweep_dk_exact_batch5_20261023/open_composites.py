#!/usr/bin/env python3
"""Write open_composites.json, open_composites.md and report/ecm_effort.svg: the 4q - t^2 still open at snapshot 5.

Reads (this directory)
  provenance/driver_state.snapshot5.json    the fifth frozen driver state: per entry the primes found, the open
                                            composites, ecm_done (tiers completed) and ecm_curves (curves counted
                                            per tier by the chunked driver, provenance/driver.snapshot5.py)
  provenance/driver_events.snapshot5.log    its event log (the last logged progress line per tier)
  provenance/survey_open.jsonl              the survey records of the open curves (small primes, composite)
  provenance/gmp_ecm_expected_curves.txt    GMP-ECM 7.0.5's own table of expected curves per B1 (ecm -v)
  provenance/factordb_status_20261023.json  FactorDB's status of each open cofactor, queried 2026-10-23
  the curve corpus (std-curves checkout), to recompute q, t and 4q - t^2
Writes
  open_composites.json, open_composites.md; with --plot, report/ecm_effort.svg from open_composites.json

Every known prime is proved prime by PARI isprime, every cofactor is checked composite, and known primes times
cofactor must give 4q - t^2 recomputed from the curve parameters.  No D_K, conductor or degree is stated.

    python3 research/endosweep_dk_exact_batch5_20261023/open_composites.py STD_CURVES_CHECKOUT \
        research/endosweep_curves_20261006
    python3 research/endosweep_dk_exact_batch5_20261023/open_composites.py --plot
"""
import json
import math
import re
import sys
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
B1DIR = HERE.parent / "endosweep_dk_exact_20261016"
sys.path.insert(0, str(B1DIR))
from build_dk_exact import load_curves, pari_isprime  # noqa: E402
from make_factorizations import method  # noqa: E402

# The driver's ECM tiers (provenance/driver.snapshot5.py, TIERS): (B1, curves per composite).
TIERS = [(11000, 90), (50000, 240), (250000, 500), (1000000, 900), (3000000, 2400), (11000000, 4480)]
DIGITS = [35, 40, 45, 50, 55, 60]
SURVEY = "PARI factor(N, 2^32) (survey, 10 s screen)"


def expected_table() -> dict[int, dict[int, float]]:
    """{B1: {digits: expected curves}} from GMP-ECM's -v output."""
    text = (HERE / "provenance/gmp_ecm_expected_curves.txt").read_text()
    out = {}
    for m in re.finditer(r"Using B1=(\d+), B2=\d+.*\n.*\n([\d\t]+)\n(\S[^\n]*)", text):
        heads = [int(x) for x in m.group(2).split()]
        vals = [float(x) for x in m.group(3).split()]       # "Inf" parses as inf
        out[int(m.group(1))] = dict(zip(heads, vals))
    assert sorted(out) == [b for b, _ in TIERS], sorted(out)
    return out


def last_progress(log: str, curve: str, B1: int) -> int | None:
    found = re.findall(rf"^\S+   B1={B1}: .*?\b{re.escape(curve)} (\d+)/\d+", log, flags=re.M)
    return int(found[-1]) if found else None


def build(std: str, ark: str) -> dict:
    snap = json.loads((HERE / "provenance/driver_state.snapshot5.json").read_text())
    log = (HERE / "provenance/driver_events.snapshot5.log").read_text()
    survey = {json.loads(l)["name"]: json.loads(l) for l in (HERE / "provenance/survey_open.jsonl").read_text().splitlines()}
    fdb = {r["curve"]: r for r in json.loads((HERE / "provenance/factordb_status_20261023.json").read_text())}
    E = expected_table()
    curves = {T.name: T for T in load_curves(std, ark)}
    rows = []
    for C, e in snap.items():
        if not e["open"]:
            continue
        name = e["curve"]
        T = curves[name]
        q, t = T.q, T.trace
        assert t == q + 1 - T.h * T.n
        N = 4 * q - t * t
        rec = survey[name]
        assert int(rec["t"]) == t and rec["4p-t^2"]["composite"] == [C]
        known = [(int(p), x, SURVEY) for p, x in rec["4p-t^2"]["known"]]
        # the driver's splits so far: each "how: n -> a x b" moved its prime parts to `primes`
        hows = [re.fullmatch(r"(.*): \d+-digit -> \d+ x \d+", line).group(1) for line in e["log"]]
        assert len(e["primes"]) <= len(hows) * 2
        for p in e["primes"]:
            assert len(hows) == 1, "one split per entry here: its method names every prime it gave"
            known.append((int(p), 1, method(hows[0])))
        assert len(e["open"]) == 1
        cof = int(e["open"][0])
        assert prod(p ** x for p, x, _ in known) * cof == N, name
        assert all(pari_isprime(p) for p, _, _ in known) and not pari_isprime(cof)
        done, counted = e["ecm_done"][str(cof)], e["ecm_curves"][str(cof)]
        # a cofactor produced by an ECM split at tier ti got only the curves run on its parent before the find
        born = {TIERS.index(next(tt for tt in TIERS if f"ECM B1={tt[0]}" == h)) for h in hows if h.startswith("ECM")}
        tiers = []
        for ti, (B1, nominal) in enumerate(TIERS):
            if ti < done:
                if str(ti) in counted:
                    n_, src = counted[str(ti)], "ecm_curves (counted per 50-curve chunk)"
                    assert n_ >= nominal
                elif ti in born:
                    n_, src = None, (f"run on the parent composite before the split that produced this cofactor; "
                                     f"count not recorded (at most {nominal})")
                else:
                    n_, src = nominal, "tier completed (ecm_done); count is the tier's nominal size, not logged"
                status = "complete"
            elif ti == done and str(ti) in counted:
                n_, src, status = counted[str(ti)], "ecm_curves (counted per 50-curve chunk)", "partial"
            else:
                continue
            tiers.append({"B1": B1, "nominal_curves": nominal, "curves": n_, "status": status, "source": src,
                          "last_logged_progress": last_progress(log, name, B1) if src.startswith("ecm_curves") else None})
        cov = {}
        for d in DIGITS:
            x = sum((tr["curves"] or 0) / E[tr["B1"]][d] for tr in tiers)
            cov[str(d)] = {"sum_curves_over_expected": round(x, 4), "miss_probability_approx": float(f"{math.exp(-x):.3g}")}
        r = fdb[name]["response"]
        assert r["factors"] == [[str(cof), 1]]
        rows.append({
            "curve": name, "p": str(q), "p_bits": q.bit_length(), "n": str(T.n), "h": T.h, "t": str(t), "N_4q_minus_t2": str(N), "N_digits": len(str(N)),
            "known_primes": [{"p": str(p), "exponent": x, "digits": len(str(p)), "found_by": how,
                              "proved_by": "PARI isprime"} for p, x, how in sorted(known)],
            "cofactor": str(cof), "cofactor_digits": len(str(cof)), "cofactor_composite": "PARI isprime is false",
            "ecm": tiers, "ecm_coverage": cov,
            "factordb": {"status": r["status"], "id": r["id"], "queried_utc": fdb[name]["queried_utc"]},
        })
    rows.sort(key=lambda r: r["cofactor_digits"])
    return {
        "question": "the 4q - t^2 values not completely factored at the fifth frozen driver snapshot",
        "snapshot": "provenance/driver_state.snapshot5.json",
        "ecm_program": "GMP-ECM 7.0.5, nice -n 5 ecm -q -one -c CURVES B1 (default B2 and parametrization)",
        "coverage_model": ("sum over tiers of curves / expected curves (GMP-ECM 7.0.5 ecm -v table, "
                           "provenance/gmp_ecm_expected_curves.txt); a d-digit factor, if one exists, is missed "
                           "by all curves with probability about exp(-sum). Uncounted curves count as 0."),
        "d_k": "not stated: these factorisations are incomplete",
        "curves": rows,
    }


def markdown(doc: dict) -> str:
    L = ["# Open composites at snapshot 5", "",
         "Generated by `open_composites.py` from `open_composites.json`.  Known primes are proved by PARI "
         "`isprime`; known primes × cofactor = 4q − t² recomputed from the curve parameters.  No D_K is stated.", "",
         "| curve | 4q−t² digits | known primes | open cofactor | B1 = 11e3 | 5e4 | 2.5e5 | 1e6 | 3e6 | 11e6 | "
         "FactorDB |", "|:--|--:|:--|--:|--:|--:|--:|--:|--:|--:|:--|"]
    for r in doc["curves"]:
        kp = " · ".join((k["p"] if k["digits"] <= 12 else f"p{k['digits']}") + (f"^{k['exponent']}" if k["exponent"] > 1
                                                                              else "") for k in r["known_primes"])
        cells = []
        for B1, nominal in TIERS:
            tr = next((x for x in r["ecm"] if x["B1"] == B1), None)
            if tr is None:
                cells.append("0")
            elif tr["curves"] is None:
                cells.append(f"≤ {nominal} (not recorded)")
            else:
                cells.append(f"{tr['curves']}" + (f" of {nominal}" if tr["status"] == "partial" else ""))
        L.append(f"| {r['curve']} | {r['N_digits']} | {kp} | C{r['cofactor_digits']} | " + " | ".join(cells)
                 + f" | {r['factordb']['status']} ({r['factordb']['queried_utc']}) |")
    L += ["", "## Coverage (GMP-ECM's expected-curve table)", "",
          "Σ curves / expected curves per factor size, and the approximate probability exp(−Σ) that a factor of "
          "that size, if one exists, was missed.", "",
          "| curve | " + " | ".join(f"{d} digits" for d in DIGITS) + " |", "|:--|" + "--:|" * len(DIGITS)]
    for r in doc["curves"]:
        L.append(f"| {r['curve']} | " + " | ".join(
            f"{r['ecm_coverage'][str(d)]['sum_curves_over_expected']:.2f} (miss ≈ "
            f"{r['ecm_coverage'][str(d)]['miss_probability_approx']:.2g})" for d in DIGITS) + " |")
    L += ["", "## Cofactors in full", ""]
    for r in doc["curves"]:
        L += [f"* **{r['curve']}** (C{r['cofactor_digits']}): `{r['cofactor']}`"]
    L += [""]
    return "\n".join(L)


def plot(doc: dict, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "svg.fonttype": "none"})
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.2))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    w = 0.2
    for i, r in enumerate(doc["curves"]):
        ys = [next((x["curves"] or 0 for x in r["ecm"] if x["B1"] == B1), 0) for B1, _ in TIERS]
        a.bar([j + (i - 1.5) * w for j in range(len(TIERS))], ys, w, color=colors[i],
              label=f"{r['curve']} (C{r['cofactor_digits']})")
    a.plot(range(len(TIERS)), [c for _, c in TIERS], "k_", ms=18, label="tier size")
    a.set_xticks(range(len(TIERS)))
    a.set_xticklabels(["11e3", "5e4", "2.5e5", "1e6", "3e6", "11e6"])
    a.set_xlabel("B1")
    a.set_ylabel("curves run on the open cofactor")
    a.set_title("(a) ECM curves per B1 tier at snapshot 5")
    a.legend(frameon=False, loc="upper left", fontsize=7.5)
    for i, r in enumerate(doc["curves"]):
        b.plot(DIGITS, [r["ecm_coverage"][str(d)]["sum_curves_over_expected"] for d in DIGITS], "o-",
               color=colors[i], ms=3, label=r["curve"])
    b.axhline(1, color="0.6", ls="--", lw=1)
    b.set_yscale("log")
    b.set_xlabel("factor size (digits)")
    b.set_ylabel("Σ curves / expected curves")
    b.set_title("(b) effort in units of expected curves")
    b.legend(frameon=False, fontsize=7.5)
    fig.text(0.01, 0.01, "Counts: driver_state.snapshot5.json. Expected curves: GMP-ECM 7.0.5 ecm -v. "
             "Dashed: 1 expected find. ed-511-mers' 11e3 curves not recorded (drawn as 0).", fontsize=7.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out)


def main(argv):
    if argv[1:] == ["--plot"]:      # the graph, from open_composites.json alone (needs matplotlib, not PARI)
        plot(json.loads((HERE / "open_composites.json").read_text()), HERE / "report/ecm_effort.svg")
        return
    doc = build(argv[1], argv[2])
    (HERE / "open_composites.json").write_text(json.dumps(doc, indent=1) + "\n")
    (HERE / "open_composites.md").write_text(markdown(doc))
    print(f"{len(doc['curves'])} open composites")


if __name__ == "__main__":
    main(sys.argv)
