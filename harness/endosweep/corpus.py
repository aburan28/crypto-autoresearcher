"""Corpus scan: every standardized prime-field curve, certified and swept.

Reads the `std-curves` database (J08nY/std-curves on GitHub: one
``<category>/curves.json`` per standard, 248 curves as of 2026-10) and turns
every prime-field curve in Weierstrass, Montgomery, Edwards or twisted
Edwards form into a registry ``Target``, which is then

1. verified from its constants (prime n, Hasse interval, a point of order
   divisible by n killed by h*n) -- a curve that fails is listed, not swept;
2. given the discriminant certificate (|D_K| > bound, or D_K found with its
   conductor), cross-checked against the database's own ``cm_disc`` and
   ``conductor`` fields where present (those were computed independently by
   the database author; agreement is a check on both);
3. for every curve with a small CM discriminant: the chain-priced cheap
   endomorphism inventory, the modelled GLV-2 speed-up, and -- for chains of
   odd primes within a step bound -- the explicit construction and point
   verification of ``explicit.py``.

Binary-field, extension-field and tower-field curves are out of scope here
(their decompositions are the Frobenius ones the sweep treats structurally)
and are listed with that reason.

    python -m harness.endosweep.corpus --std-curves /path/to/std-curves --out-dir research/endosweep_20261005/corpus
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import time
from dataclasses import asdict, dataclass, field

from . import quadorder as QO
from .targets import Target, verify


def _int(raw) -> int:
    """A database integer: decimal or 0x-hex, optionally signed ("-0x05" is
    Bandersnatch's twisted-Edwards a)."""
    if isinstance(raw, dict):
        raw = raw.get("raw")
    s = str(raw).strip()
    neg = s.startswith("-")
    if neg or s.startswith("+"):
        s = s[1:].strip()
    v = int(s, 16) if s.lower().startswith("0x") else int(s)
    return -v if neg else v


@dataclass
class CorpusEntry:
    name: str
    category: str
    form: str
    field_type: str
    bits: int
    skipped: str = ""
    verified: bool | None = None
    verification: str = ""
    scan_D: int | None = None
    scan_conductor: int | None = None
    scan_certificate: str = ""
    db_cm_disc: int | None = None
    db_conductor: int | None = None
    db_agreement: str = ""
    class_number: int | None = None
    min_nonscalar_degree: int | None = None
    cheapest_chain: dict | None = None
    best_config: dict | None = None
    generic_cost_M: float | None = None
    explicit: dict | None = None
    elapsed_s: float = 0.0


def load_std_curves(root: str) -> list[tuple[Target | None, CorpusEntry, dict]]:
    out = []
    for path in sorted(glob.glob(os.path.join(root, "*", "curves.json"))):
        category = os.path.basename(os.path.dirname(path))
        data = json.load(open(path))
        for c in data.get("curves", []):
            name = f"{category}/{c['name']}"
            ftype = c["field"]["type"]
            form = c.get("form", "")
            bits = int(c["field"].get("bits", 0) or 0)
            entry = CorpusEntry(name, category, form, ftype, bits)
            if ftype != "Prime":
                entry.skipped = f"field type {ftype}: outside the prime-field pipeline"
                out.append((None, entry, c))
                continue
            try:
                p = _int(c["field"]["p"])
                n = _int(c["order"])
                h = _int(c.get("cofactor", "0x1"))
                params = c["params"]
                if form == "Weierstrass":
                    T = Target(name, p, "weierstrass", {"a": _int(params["a"]), "b": _int(params["b"])}, n, h,
                               cost_model="weierstrass_jacobian_a=-3" if (_int(params["a"]) - (p - 3)) % p == 0
                               else "weierstrass_jacobian_a=0" if _int(params["a"]) % p == 0
                               else "weierstrass_jacobian_generic_a", family=f"corpus:{category}")
                elif form == "Montgomery":
                    T = Target(name, p, "montgomery", {"A": _int(params["a"]), "B": _int(params["b"])}, n, h,
                               cost_model="twisted_edwards_a=-1_extended", family=f"corpus:{category}")
                elif form == "TwistedEdwards":
                    T = Target(name, p, "edwards", {"a": _int(params["a"]), "d": _int(params["d"])}, n, h,
                               cost_model="twisted_edwards_a=-1_extended", family=f"corpus:{category}")
                elif form == "Edwards":
                    # x^2 + y^2 = c^2 (1 + d x^2 y^2)  ->  x'^2 + y'^2 = 1 + d c^4 x'^2 y'^2 with x = c x'
                    cc = _int(params["c"]) % p
                    dd = _int(params["d"]) * pow(cc, 4, p) % p
                    T = Target(name, p, "edwards", {"a": 1, "d": dd}, n, h,
                               cost_model="twisted_edwards_a=-1_extended", family=f"corpus:{category}")
                else:
                    entry.skipped = f"form {form}: not handled"
                    out.append((None, entry, c))
                    continue
                T.notes = "; ".join(s.get("name", "") for s in c.get("sources", []))
                ch = c.get("characteristics", {}) or {}
                if ch.get("cm_disc") not in (None, ""):
                    entry.db_cm_disc = int(ch["cm_disc"])
                if ch.get("conductor") not in (None, ""):
                    entry.db_conductor = int(ch["conductor"])
                out.append((T, entry, c))
            except Exception as e:  # noqa: BLE001
                entry.skipped = f"could not parse: {e}"
                out.append((None, entry, c))
    return out


def scan_entry(T: Target, entry: CorpusEntry, *, disc_bound: int, explicit_max_prime: int,
               explicit_time_budget_s: float) -> CorpusEntry:
    from .sweep import SweepOptions, build_catalogue, sweep_target
    t0 = time.time()
    verify(T)
    entry.verified, entry.verification = T.verified, T.verification
    if not T.verified:
        entry.elapsed_s = time.time() - t0
        return entry
    Dfrob = QO.frobenius_discriminant(T.q, T.trace)
    if Dfrob >= 0:
        entry.scan_certificate = "t^2 - 4q >= 0: not an ordinary curve with |t| <= 2 sqrt q; skipped"
        entry.elapsed_s = time.time() - t0
        return entry
    scan = QO.small_discriminant_scan(Dfrob, disc_bound)
    entry.scan_D, entry.scan_conductor, entry.scan_certificate = scan.found, scan.conductor, scan.certificate
    # cross-check with the database's independently computed CM data
    if entry.db_cm_disc is not None:
        if scan.found is None:
            entry.db_agreement = ("agree: database |cm_disc| is above the scan bound"
                                  if abs(entry.db_cm_disc) > disc_bound else
                                  f"DISAGREE: database says {entry.db_cm_disc}, scan found nothing below {disc_bound}")
        else:
            db_D, db_f = entry.db_cm_disc, entry.db_conductor
            # the database may list a non-fundamental discriminant; compare the product D f^2
            ok_D = (db_D == scan.found) or (db_f is not None and db_D * db_f * db_f == scan.found * scan.conductor ** 2)
            entry.db_agreement = "agree" if ok_D else f"DISAGREE: database {db_D} (conductor {db_f}) vs scan {scan.found} (conductor {scan.conductor})"
    else:
        entry.db_agreement = "database has no cm_disc"
    if scan.found is not None:
        D = scan.found
        opts = SweepOptions(max_dim=2, pump_primes=(), lattice_samples=8)
        res = sweep_target(T, opts)
        entry.class_number = res.class_number
        entry.min_nonscalar_degree = res.min_nonscalar_degree
        iso = [c for c in res.cheap_endomorphisms if c.get("kind") == "isogeny"]
        if iso:
            cheapest = min(iso, key=lambda c: c["cost_M"])
            entry.cheapest_chain = {k: cheapest[k] for k in ("name", "degree", "cost_M", "a", "b", "chain")}
        best = res.configs[0]
        entry.best_config = {"label": best.label, "cost_M": best.cost_M, "speedup": best.speedup_vs_generic,
                             "coeff_bits": best.coeff_bits_empirical, "known_as": best.known_as}
        entry.generic_cost_M = res.generic_cost_M
        # explicit construction of the cheapest chain when it is a chain of small odd primes
        if entry.cheapest_chain is not None and T.model == "weierstrass":
            from sympy import factorint
            from .explicit import build_chain_endomorphism
            deg = entry.cheapest_chain["degree"]
            fac = factorint(deg)
            if all(2 < ell <= explicit_max_prime for ell in fac):
                import signal

                def _alarm(signum, frame):
                    raise TimeoutError("explicit construction exceeded its time budget")

                old = signal.signal(signal.SIGALRM, _alarm)
                signal.alarm(int(explicit_time_budget_s))
                try:
                    r = build_chain_endomorphism(T.p, T.coeffs["a"], T.coeffs["b"], T.n, T.h, D,
                                                 (entry.cheapest_chain["a"], entry.cheapest_chain["b"]),
                                                 curve_name=T.name)
                    entry.explicit = {"found": r.found, "steps": r.steps, "degree": r.degree,
                                      "walks_examined": r.walks_examined, "glv_check": r.glv_check,
                                      "note": r.note}
                except TimeoutError as e:
                    entry.explicit = {"found": None, "note": str(e)}
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old)
            else:
                entry.explicit = {"found": None,
                                  "note": f"chain {entry.cheapest_chain['chain']} has a step outside the explicit "
                                          f"builder's scope (odd primes <= {explicit_max_prime})"}
    entry.elapsed_s = time.time() - t0
    return entry


def markdown(entries: list[CorpusEntry], disc_bound: int) -> str:
    L = ["# Standardized-curve corpus scan\n",
         f"Source: std-curves database. Certificate bound |D_K| <= {disc_bound}. "
         "Costs are operation counts under the sweep's model.\n"]
    swept = [e for e in entries if e.verified]
    hits = [e for e in swept if e.scan_D is not None]
    clean = [e for e in swept if e.scan_D is None and e.scan_certificate.startswith("no fundamental")]
    L.append(f"- curves in corpus: {len(entries)}; prime-field and verified: {len(swept)}; "
             f"certified |D_K| > {disc_bound}: {len(clean)}; small CM discriminant: {len(hits)}; "
             f"skipped (binary/extension/tower/unparsed): {sum(1 for e in entries if e.skipped)}; "
             f"failed verification: {sum(1 for e in entries if e.verified is False)}")
    agree = sum(1 for e in swept if e.db_agreement.startswith("agree"))
    disagree = [e for e in swept if e.db_agreement.startswith("DISAGREE")]
    L.append(f"- cross-check against the database's own cm_disc: {agree} agree, {len(disagree)} disagree, "
             f"{sum(1 for e in swept if e.db_agreement == 'database has no cm_disc')} without database data\n")
    L.append("## Curves with a small CM discriminant\n")
    L.append("| curve | bits | form | D_K | h(D) | min degree | cheapest chain | chain M | modelled best | total M | generic M | speedup | explicit chain |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in sorted(hits, key=lambda e: (e.category, e.name)):
        cc = e.cheapest_chain or {}
        bc = e.best_config or {}
        ex = e.explicit or {}
        exs = ("verified on points" if ex.get("found") else ("FAILED: " + ex.get("note", "")) if ex.get("found") is False
               else ex.get("note", "not attempted"))
        L.append(f"| {e.name} | {e.bits} | {e.form} | {e.scan_D} | {e.class_number} | {e.min_nonscalar_degree} | "
                 f"{cc.get('chain', '')} | {cc.get('cost_M', 0):.0f} | {bc.get('label', '')} | {bc.get('cost_M', 0):.0f} | "
                 f"{e.generic_cost_M or 0:.0f} | {bc.get('speedup', 0):.2f}x | {exs} |")
    L.append("")
    if disagree:
        L.append("## Disagreements with the database\n")
        for e in disagree:
            L.append(f"- {e.name}: {e.db_agreement}")
        L.append("")
    L.append("## Every prime-field curve\n")
    L.append("| curve | bits | form | verified | certificate | database cm_disc | agreement |")
    L.append("|---|---|---|---|---|---|---|")
    for e in sorted(entries, key=lambda e: (e.category, e.name)):
        if e.skipped:
            L.append(f"| {e.name} | {e.bits} | {e.form} | skipped | {e.skipped} | | |")
            continue
        cert = (f"D_K = {e.scan_D}, conductor {e.scan_conductor}" if e.scan_D is not None else
                (f"|D_K| > {disc_bound}" if e.scan_certificate.startswith("no fundamental") else e.scan_certificate))
        L.append(f"| {e.name} | {e.bits} | {e.form} | {e.verified} | {cert if e.verified else e.verification} | "
                 f"{e.db_cm_disc if e.db_cm_disc is not None else ''} | {e.db_agreement} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="scan a std-curves checkout")
    ap.add_argument("--std-curves", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--disc-bound", type=int, default=2_000_000)
    ap.add_argument("--explicit-max-prime", type=int, default=31)
    ap.add_argument("--explicit-time-budget", type=float, default=120.0)
    ap.add_argument("--only", default=None, help="substring filter on curve names")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    loaded = load_std_curves(args.std_curves)
    entries: list[CorpusEntry] = []
    for T, entry, raw in loaded:
        if args.only and args.only.lower() not in entry.name.lower():
            continue
        if T is None:
            entries.append(entry)
            continue
        e = scan_entry(T, entry, disc_bound=args.disc_bound, explicit_max_prime=args.explicit_max_prime,
                       explicit_time_budget_s=args.explicit_time_budget)
        entries.append(e)
        flag = (f"D_K={e.scan_D} h={e.class_number} best={e.best_config['label'] if e.best_config else ''}"
                if e.scan_D is not None else ("clean" if e.verified else "FAILED"))
        print(f"[{e.elapsed_s:6.1f}s] {e.name:40s} {e.bits:4d} {flag} | db: {e.db_agreement}")
    with open(os.path.join(args.out_dir, "corpus.json"), "w") as f:
        json.dump([asdict(e) for e in entries], f, indent=1, default=str)
    with open(os.path.join(args.out_dir, "corpus.md"), "w") as f:
        f.write(markdown(entries, args.disc_bound))
    print(f"wrote {args.out_dir}/corpus.json and corpus.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
