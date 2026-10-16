#!/usr/bin/env python3
"""Assemble factorizations.jsonl: the complete factorisations of 4q - t^2 the survey and the driver found.

Reads
  provenance/survey_selected.jsonl     the survey records (survey.py) of the curves below: the small primes
                                       PARI factor(N, 2^32) found, and the composite cofactor it left
  provenance/driver_state.snapshot.json the frozen state of driver.py: per composite C, the primes it was
                                       split into, what is still open, and a log line per split
  the curve corpus (std-curves checkout and the arkworks curves.json root), to recompute q and t
Writes
  factorizations.jsonl                 one record per curve whose snapshot entry has open == [],
                                       except the four already certified in research/endosweep_nist_20261006

Every record is checked before it is written: the factors multiply back to 4q - t^2 exactly and every factor
is proved prime by PARI isprime (a proof, not a pseudoprime test).  Which method found each factor is
reconstructed by replaying the snapshot's split log; a split the replay cannot place stops the script.

    python3 research/endosweep_dk_exact_20261016/make_factorizations.py STD_CURVES_CHECKOUT \
        research/endosweep_curves_20261006
"""
import json
import re
import sys
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_dk_exact import EXCLUDED_NIST, load_curves, pari_isprime  # noqa: E402

ECM = "GMP-ECM 7.0.5"
CADO = "CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b)"
TIER = {"11000": 1, "50000": 2, "250000": 3, "1000000": 4}


def method(how: str) -> str:
    m = re.fullmatch(r"ECM B1=(\d+)", how)
    if m:
        return f"{ECM} B1={m.group(1)} (driver tier {TIER[m.group(1)]})"
    m = re.fullmatch(r"CADO-NFS \((\d+) s wall\)", how)
    if m:
        return f"{CADO}, cado-nfs.py C -t 4 ({m.group(1)} s wall)"
    m = re.fullmatch(r"PARI factorint \((\d+) s\)", how)
    if m:
        return f"PARI factorint ({m.group(1)} s)"
    raise ValueError(f"unknown split method {how!r}")


def _replays(open_: list[int], primes: list[int], log: list[str], found: dict[int, str], seq: list[int]):
    """Every assignment of primes to splits consistent with the log and with the order of `primes`.

    driver.split appends the prime parts of each split to the entry's `primes` in the order the splits
    happened (first the found factor, then the cofactor), so a replay must reproduce that list exactly.
    """
    if seq != primes[:len(seq)]:
        return
    if not log:
        if not open_ and seq == primes:
            yield dict(found)
        return
    line = log[0]
    m = re.fullmatch(r"(.*): (\d+)-digit -> (\d+) x (\d+)", line)
    if not m:
        raise ValueError(f"unparsed log line {line!r}")
    how, nd, a, b = m.group(1), *map(int, m.groups()[1:])
    for n in [n for n in open_ if len(str(n)) == nd]:
        # the split part f is a product of a sub-multiset of the primes dividing n, with a digits
        ps = [p for p in primes if n % p == 0]
        hits = set()
        for mask in range(1, 1 << len(ps)):
            f = prod(p for i, p in enumerate(ps) if mask >> i & 1)
            if n % f == 0 and len(str(f)) == a and len(str(n // f)) == b:
                hits.add(min(f, n // f))      # a = b: the two parts are interchangeable
        for f in sorted(hits):
            # the part the method returned comes first (a digits); when a = b either may be it
            for first in sorted({x for x in (f, n // f) if len(str(x)) == a}):
                rest, new, nseq = [x for x in open_ if x != n], dict(found), list(seq)
                for part in (first, n // first):
                    if part in primes:
                        new[part] = method(how)
                        nseq.append(part)
                    else:
                        rest.append(part)
                yield from _replays(rest, primes, log[1:], new, nseq)


def replay(C: int, primes: list[int], log: list[str]) -> dict[int, str]:
    """Which split produced each prime of C: replay 'how: n-digit -> a x b' over the primes.

    The log records digit counts, not the factors; the order of `primes` settles which split found
    which prime.  Should several replays still fit, a prime gets every method they allow, joined by
    ' or '.
    """
    sols = list(_replays([C], primes, log, {}, []))
    if not sols:
        raise ValueError(f"no replay of {log} fits {primes}")
    out = {}
    for p in set(primes):
        ms = sorted({s[p] for s in sols})
        out[p] = " or ".join(ms)
    return out


def main(argv):
    std, ark = argv[1], argv[2]
    curves = {T.name: T for T in load_curves(std, ark)}
    survey = {}
    for line in open(HERE / "provenance/survey_selected.jsonl"):
        r = json.loads(line)
        survey[r["name"]] = r
    snap = json.load(open(HERE / "provenance/driver_state.snapshot.json"))
    out = []
    for C, e in snap.items():
        if e["open"] or e["curve"] in EXCLUDED_NIST:
            continue
        T = curves[e["curve"]]
        q, t = T.q, T.trace
        N = 4 * q - t * t
        rec = survey[e["curve"]]
        assert int(rec["t"]) == t and rec["4p-t^2"]["status"] == "CF"
        assert rec["4p-t^2"]["composite"] == [C]
        known = [(int(p), x) for p, x in rec["4p-t^2"]["known"]]
        C = int(C)
        cps = [int(p) for p in e["primes"]]
        assert prod(cps) == C
        # The survey kept the composite cofactor but not its exponent: on the D = -3 curves (BN, BLS12, BW6)
        # 4q - t^2 = 3 f^2, so the partial factorisation leaves C^2.  Recover the exponent by division.
        rest, ec = N, 0
        assert rest % prod(p ** x for p, x in known) == 0
        rest //= prod(p ** x for p, x in known)
        while rest % C == 0:
            rest //= C
            ec += 1
        assert rest == 1 and ec >= 1, e["curve"]
        by = replay(C, cps, e["log"])
        fac: dict[int, int] = {}
        how: dict[int, str] = {}
        for p, x in known:
            fac[p] = fac.get(p, 0) + x
            how[p] = "PARI factor(N, 2^32) (survey, 10 s screen)"
        for p in cps:
            fac[p] = fac.get(p, 0) + ec
            how.setdefault(p, by[p])
        factors = sorted(fac.items())
        assert prod(p ** x for p, x in factors) == N
        assert all(pari_isprime(p) for p, _ in factors)
        out.append({"curve": e["curve"], "N": str(N), "factors": [[str(p), x] for p, x in factors],
                    "found_by": [how[p] for p, _ in factors], "seconds": None,
                    "primes_proven_by": "PARI isprime"})
    out.sort(key=lambda r: (int(r["N"]).bit_length(), r["curve"]))
    with open(HERE / "factorizations.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(out)} certificates")


if __name__ == "__main__":
    main(sys.argv)
