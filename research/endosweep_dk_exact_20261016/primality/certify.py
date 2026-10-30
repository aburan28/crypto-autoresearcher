#!/usr/bin/env python3
"""Produce and check ECPP certificates for the D_K-exact factors above 10^8.

Which numbers: every factor `p > 10^8` that appears in a `factors := [...]`
list of `formal/CryptoResearch/Endosweep/DkExact*.lean` (odd AND even
exponent), plus every factor `p > 10^8` in `../factorizations.jsonl`.  The
odd-exponent ones are exactly the cards' `largePrimes`, the hypothesis of
`DkCert.Statement`'s fundamentality clause; the even-exponent ones are
listed too because the README states every factor is prime.  The script
refuses to run if a `largePrimes` entry is missing from the `factors` list
or if a JSONL factor is not in a Lean card.

What it does, per number:
  1. PARI/GP `primecert(N)` (ECPP, flag 0) and `primecertisvalid` on it;
  2. writes `certificates/<N>.json` (canonical JSON, sorted keys);
  3. runs `verify_ecpp.py`, which shares no code with PARI, on that file;
  4. records both verdicts and the certificate's SHA-256 in `manifest.json`.

For `N < 2^64` PARI's `primecert` returns `N` itself (BPSW is a proof
there); such a certificate is stored as `kind: small` and the independent
checker proves it with a Pratt certificate instead.

Usage:  python3 certify.py            (re-creates certificates/ and manifest.json)
Exit status 0 iff every number is certified by both checkers.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = HERE.parent
THRESHOLD = 10**8

sys.path.insert(0, str(HERE))
import verify_ecpp  # noqa: E402


def collect() -> dict[int, list[dict]]:
    found: dict[int, list[dict]] = {}
    cards = 0
    for path in sorted((ROOT / "formal/CryptoResearch/Endosweep").glob("DkExact*.lean")):
        text = path.read_text()
        rel = str(path.relative_to(ROOT))
        for blk in re.finditer(r"def (\w+) : DkCert where(.*?)(?=\ntheorem|\ndef |\Z)", text, re.S):
            cards += 1
            card, body = blk.group(1), blk.group(2)
            fac = re.search(r"factors := \[(.*?)\]\n", body, re.S).group(1)
            large = {int(x) for x in re.findall(r"\d+", re.search(r"largePrimes := \[(.*?)\]", body, re.S).group(1))}
            odd_large = set()
            for p, e in re.findall(r"\((\d+), (\d+)\)", fac):
                p, e = int(p), int(e)
                if p > THRESHOLD:
                    if e % 2:
                        odd_large.add(p)
                    found.setdefault(p, []).append(
                        {"source": rel, "card": card, "exponent": e, "in_largePrimes": p in large})
            if large != odd_large:
                raise SystemExit(f"{rel}:{card}: largePrimes != odd-exponent factors above 10^8")
    n_decl = sum(len(re.findall(r"^def \w+ : DkCert where", p.read_text(), re.M))
                 for p in (ROOT / "formal/CryptoResearch/Endosweep").glob("DkExact*.lean"))
    if cards != n_decl:
        raise SystemExit(f"parsed {cards} cards but {n_decl} are declared")
    for line in (DATA / "factorizations.jsonl").read_text().splitlines():
        rec = json.loads(line)
        for p, e in rec["factors"]:
            p = int(p)
            if p > THRESHOLD:
                if p not in found:
                    raise SystemExit(f"JSONL factor {p} ({rec['curve']}) is in no Lean card")
                found[p].append({"source": str((DATA / "factorizations.jsonl").relative_to(ROOT)),
                                 "card": rec["curve"], "exponent": e})
    return dict(sorted(found.items()))


GP_PROGRAM = r"""
default(parisizemax, 2^31);
{
  my(L = readvec("%s"));
  for(i = 1, #L,
    my(N = L[i], c = primecert(N), v = primecertisvalid(c));
    print(N, ";", v, ";", c));
}
"""


def run_pari(numbers: list[int]) -> dict[int, tuple[int, object]]:
    work = HERE / ".work"
    work.mkdir(exist_ok=True)
    (work / "numbers.gp").write_text("\n".join(map(str, numbers)) + "\n")
    out = subprocess.run(["gp", "-q", "-f"], input=GP_PROGRAM % (work / "numbers.gp"),
                         capture_output=True, text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        n, v, c = line.split(";", 2)
        res[int(n)] = (int(v), json.loads(c))
    for f in work.iterdir():
        f.unlink()
    work.rmdir()
    return res


def gp_version() -> str:
    return subprocess.run(["gp", "-q", "-f"], input="print(version())", capture_output=True,
                          text=True, check=True).stdout.strip()


def main() -> int:
    factors = collect()
    pari = run_pari(list(factors))
    certdir = HERE / "certificates"
    certdir.mkdir(exist_ok=True)
    for f in certdir.glob("*.json"):
        f.unlink()
    rng = random.Random(20261029)
    rows, failures = [], []
    for N, sources in factors.items():
        v_pari, c = pari[N]
        if isinstance(c, int):
            if c != N:
                raise SystemExit(f"primecert({N}) returned {c}")
            cert = {"N": str(N), "kind": "small"}
        else:
            cert = {"N": str(N), "kind": "ecpp",
                    "steps": [[str(s[0]), str(s[1]), str(s[2]), str(s[3]), [str(s[4][0]), str(s[4][1])]]
                              for s in c]}
        blob = (json.dumps(cert, sort_keys=True, separators=(",", ":")) + "\n").encode()
        path = certdir / f"{N}.json"
        path.write_bytes(blob)
        try:
            r = verify_ecpp.check_certificate(json.loads(blob), rng)
            v_ind, reason = r["valid"], None
        except verify_ecpp.Invalid as e:
            v_ind, reason = False, str(e)
        row = {
            "factor": str(N),
            "digits": len(str(N)),
            "certificate": f"certificates/{N}.json",
            "certificate_sha256": hashlib.sha256(blob).hexdigest(),
            "certificate_kind": cert["kind"],
            "ecpp_steps": len(cert.get("steps", [])),
            "pari_primecertisvalid": bool(v_pari),
            "independent_verify_ecpp": bool(v_ind),
            "used_by": sources,
        }
        if reason:
            row["independent_failure"] = reason
        rows.append(row)
        if not (v_pari and v_ind):
            failures.append(N)
    manifest = {
        "schema": "crypto.autoresearch.primality_manifest.v1",
        "scope": "every factor > 10^8 in a factors list of formal/CryptoResearch/Endosweep/DkExact*.lean "
                 "and in research/endosweep_dk_exact_20261016/factorizations.jsonl",
        "pari_version": gp_version(),
        "pari_producer": "primecert(N) (ECPP, flag 0); checked by primecertisvalid",
        "independent_checker": "verify_ecpp.py (Goldwasser-Kilian/Atkin-Morain steps + Pratt for the final q; no PARI)",
        "count": len(rows),
        "count_in_largePrimes": sum(any(s.get("in_largePrimes") for s in r["used_by"]) for r in rows),
        "certified_by_both": len(rows) - len(failures),
        "failures": [str(n) for n in failures],
        "factors": rows,
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{manifest['certified_by_both']}/{manifest['count']} certified by both checkers;"
          f" failures: {manifest['failures']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
