#!/usr/bin/env python3
"""Independently re-verify every claimed discrete-log or decomposition
certificate under experiments/*/runs/.

docs/claims-and-verification.md requires that a claimed solve or relation be
re-checked "with code independent of the solver" before a run counts as
`completed_valid`. No existing gate does that recomputation: the ledger
validator only checks that a boolean is present and true --

    if cert.get("verified") is not True:
        ctx.err(path, f"run claims a {kind} but certificate.verified is not true")

  (tools/validate_ledger.py) -- which trusts whatever the run wrapper wrote
about itself. A solver that returns a wrong `k` and writes `verified: true`
passes that check today. This tool recomputes the math instead.

INDEPENDENCE. This module shares no code with harness/ or src/. A verifier
built from the same curve-arithmetic module as the solver cannot catch a bug
in that module -- independence from the code under test is the entire point
of the certificate discipline docs/claims-and-verification.md describes, and
matters here twice as much as in an ordinary test suite.

TWO ON-DISK FORMATS. Certificate statements live in two places, and both are
walked because a manifest's claim may be backed by either:
  - experiments/*/runs/*/raw-result.json -- a single top-level 'certificate'
    key (the format docs/claims-and-verification.md documents).
  - experiments/*/runs/*/certificates.json -- a batch format: a list of
    per-target certificates under 'certificates', used by higher-volume runs
    (e.g. EXP-RT1476-001, which claims hundreds of relations per run). Its
    'certificate_kind'/'count' fields summarize the list but carry no
    statement of their own.
A run's manifest.yaml declares one certificate kind; this tool treats the
claim as backed if a matching, independently-verifying statement exists in
EITHER file, and as an error if neither has one.

BASELINE. A raw-result.json or certificates.json that fails to parse is
grandfathered ONLY by exact path in tools/verify_certificates_baseline.txt,
by the same prune-only discipline as tools/merge_hygiene_baseline.txt: this
check exists specifically to catch claims nothing else looks at, so quietly
skipping an unparseable one on an ongoing basis would defeat it.

Usage:
    python3 tools/verify_certificates.py
    python3 tools/verify_certificates.py --update-baseline

Exit 0 if every certificate (grandfathered files aside) independently
reverifies and every kind-bearing manifest claim is backed by one; 1
otherwise.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_ledger as vl  # single source of truth for REPO, load_yaml

REPO = vl.REPO

BASELINE_PATH = os.path.join(REPO, "tools", "verify_certificates_baseline.txt")
BASELINE_HEADER = """\
# Run artifacts that already failed to parse when this gate was introduced.
# One repo-relative path per line. Grandfathered ONLY so the gate could be
# turned on at all -- these are defects, not exemptions, and run artifacts
# are immutable (AGENTS.md rule 4): a listed file is repaired by superseding
# its RUN id, never by editing the file this baseline points at.
#
# Lines may only ever be REMOVED, as runs are superseded or repaired. Adding
# a line to silence a new failure defeats the entire point of the check.
# Prune stale lines with: python3 tools/verify_certificates.py --update-baseline
"""

CLAIM_KINDS = {"discrete_log", "decomposition"}
ALL_KINDS = CLAIM_KINDS | {"none"}


# --- self-contained short-Weierstrass arithmetic -- do not import from
# harness/ or src/; see module docstring. ---------------------------------

def _pt(v):
    if v is None:
        return None
    if not (isinstance(v, (list, tuple)) and len(v) == 2):
        raise ValueError(f"point must be a 2-element [x, y], got {v!r}")
    return (int(v[0]), int(v[1]))


def _on_curve(p: int, a: int, b: int, P) -> bool:
    if P is None:  # point at infinity
        return True
    x, y = P
    return (y * y - x * x * x - a * x - b) % p == 0


def _add(p: int, a: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        denom = (2 * y1) % p
        if denom == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(denom, -1, p) % p
    else:
        denom = (x2 - x1) % p
        if denom == 0:
            raise ValueError("distinct points share an x-coordinate "
                             "(non-curve input or p not prime)")
        lam = (y2 - y1) * pow(denom, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def _mul(p: int, a: int, k: int, P):
    if k < 0:
        raise ValueError("certificate k must be non-negative")
    R, Q = None, P
    while k > 0:
        if k & 1:
            R = _add(p, a, R, Q)
        Q = _add(p, a, Q, Q)
        k >>= 1
    return R


def _curve_params(statement: dict) -> tuple[int, int, int]:
    curve = statement.get("curve") or {}
    for field in ("p", "a", "b"):
        if field not in curve:
            raise ValueError(f"statement.curve missing '{field}'")
    p, a, b = int(curve["p"]), int(curve["a"]), int(curve["b"])
    if p < 5:
        raise ValueError(f"statement.curve.p = {p} is too small to be a field")
    return p, a, b


def verify_statement(kind: str, statement: dict) -> None:
    """Raise ValueError/AssertionError if `statement` does not independently
    verify as a `kind` certificate. Returns normally on success."""
    if kind not in CLAIM_KINDS:
        raise ValueError(f"not a claim-bearing kind: {kind!r}")
    p, a, b = _curve_params(statement)

    if kind == "discrete_log":
        for field in ("P", "Q", "k"):
            if field not in statement:
                raise ValueError(f"discrete_log statement missing '{field}'")
        P, Q, k = _pt(statement["P"]), _pt(statement["Q"]), int(statement["k"])
        for name, point in (("P", P), ("Q", Q)):
            if not _on_curve(p, a, b, point):
                raise AssertionError(f"{name}={point} is not on curve "
                                     f"y^2=x^3+{a}x+{b} mod {p}")
        got = _mul(p, a, k, P)
        if got != Q:
            raise AssertionError(f"k*P recomputes to {got}, but the "
                                 f"certificate claims Q={Q}")
    else:  # decomposition
        for field in ("target", "summands"):
            if field not in statement:
                raise ValueError(f"decomposition statement missing '{field}'")
        target = _pt(statement["target"])
        summands = [_pt(s) for s in statement["summands"]]
        for name, point in (("target", target),
                            *((f"summand[{i}]", s) for i, s in enumerate(summands))):
            if not _on_curve(p, a, b, point):
                raise AssertionError(f"{name}={point} is not on curve "
                                     f"y^2=x^3+{a}x+{b} mod {p}")
        acc = None
        for s in summands:
            acc = _add(p, a, acc, s)
        if acc != target:
            raise AssertionError(f"sum of summands recomputes to {acc}, "
                                 f"but the certificate claims target={target}")


# --- repository walk -------------------------------------------------------

def _baseline() -> set[str]:
    try:
        with open(BASELINE_PATH, "r", encoding="utf-8") as fh:
            return {ln.strip() for ln in fh
                    if ln.strip() and not ln.startswith("#")}
    except OSError:
        return set()


def _write_baseline(entries: set[str]) -> None:
    with open(BASELINE_PATH, "w", encoding="utf-8") as fh:
        fh.write(BASELINE_HEADER)
        for e in sorted(entries):
            fh.write(e + "\n")


def _load_json(path: str):
    """Return (doc, error) -- error is None on success."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, None
    except Exception as exc:
        return None, str(exc).strip().splitlines()[0]


def check() -> tuple[list[str], set[str]]:
    """Returns (errors, currently_unparseable_relpaths)."""
    errors: list[str] = []
    unparseable: set[str] = set()
    grandfathered = _baseline()
    stale = set(grandfathered)

    for manifest_path in sorted(glob.glob(os.path.join(
            REPO, "experiments", "*", "runs", "*", "manifest.yaml"))):
        run_dir = os.path.dirname(manifest_path)
        rel_manifest = os.path.relpath(manifest_path, REPO)

        doc = vl.load_yaml(manifest_path, vl.Ctx(set()))
        run = (doc or {}).get("run") if isinstance(doc, dict) else None
        if not isinstance(run, dict):
            continue  # validate_ledger.py already reports this
        declared_kind = ((run.get("result") or {}).get("certificate") or {}).get("kind")
        if declared_kind is not None and declared_kind not in ALL_KINDS:
            errors.append(f"{rel_manifest}: certificate.kind {declared_kind!r} "
                          f"is not one of {sorted(ALL_KINDS)}")
            declared_kind = None

        raw_path = os.path.join(run_dir, "raw-result.json")
        rel_raw = os.path.relpath(raw_path, REPO)
        raw_doc, raw_err = _load_json(raw_path)
        if raw_err is not None:
            unparseable.add(rel_raw)
            if rel_raw in grandfathered:
                stale.discard(rel_raw)
            else:
                errors.append(f"{rel_raw}: does not parse as JSON: {raw_err}")

        certs_path = os.path.join(run_dir, "certificates.json")
        rel_certs = os.path.relpath(certs_path, REPO)
        certs_doc, certs_err = _load_json(certs_path)
        if certs_err is not None:
            unparseable.add(rel_certs)
            if rel_certs in grandfathered:
                stale.discard(rel_certs)
            else:
                errors.append(f"{rel_certs}: does not parse as JSON: {certs_err}")

        # Gather every independently-checkable statement this run offers,
        # from whichever of the two formats supplies it.
        statements: list[tuple[str, str, dict]] = []  # (source, kind, statement)
        if isinstance(raw_doc, dict):
            cert = raw_doc.get("certificate")
            if isinstance(cert, dict):
                kind = cert.get("kind")
                if kind in ALL_KINDS and kind != "none":
                    st = cert.get("statement")
                    if isinstance(st, dict):
                        statements.append((rel_raw, kind, st))
                elif kind is not None and kind not in ALL_KINDS:
                    errors.append(f"{rel_raw}: certificate.kind {kind!r} is "
                                  f"not one of {sorted(ALL_KINDS)}")
        if isinstance(certs_doc, dict):
            for c in certs_doc.get("certificates") or []:
                if not isinstance(c, dict):
                    continue
                kind = c.get("kind")
                st = c.get("statement")
                cid = c.get("certificate_id", "<no id>")
                if kind in CLAIM_KINDS and isinstance(st, dict):
                    statements.append((f"{rel_certs}#{cid}", kind, st))
                elif kind is not None and kind not in ALL_KINDS:
                    errors.append(f"{rel_certs}#{cid}: certificate.kind "
                                  f"{kind!r} is not one of {sorted(ALL_KINDS)}")

        # Independently re-verify every statement found, regardless of what
        # the manifest declares -- a statement present but unverifiable is a
        # defect even if nothing ever cross-references it.
        for source, kind, st in statements:
            try:
                verify_statement(kind, st)
            except Exception as exc:
                errors.append(f"{source}: {kind} certificate FAILED "
                              f"independent reverification: {exc}")

        # Cross-check: a manifest claiming a claim-bearing kind with a
        # nonzero count must be backed by at least one statement of that
        # kind somewhere. count: 0 (e.g. a negative control that certified
        # zero relations) legitimately has nothing to back and is not an
        # error -- the absence of statements IS the claim in that case.
        declared_count = ((run.get("result") or {}).get("certificate") or {}).get("count")
        if declared_kind in CLAIM_KINDS and declared_count != 0:
            backing = [s for s in statements if s[1] == declared_kind]
            if not backing:
                errors.append(
                    f"{rel_manifest}: run claims kind={declared_kind!r} "
                    f"(count={declared_count!r}) but no verifiable statement "
                    f"for it exists in {rel_raw} or {rel_certs}")

    for rel in sorted(stale):
        print(f"note: {rel} now parses; drop it from "
              f"tools/verify_certificates_baseline.txt", file=sys.stderr)

    return errors, unparseable


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update-baseline", action="store_true",
                    help="rewrite the baseline to exactly the currently "
                         "unparseable run artifacts (prune-only in normal "
                         "use; this is the one command allowed to grow it, "
                         "and only for files that already fail today)")
    args = ap.parse_args()

    errors, unparseable = check()

    if args.update_baseline:
        _write_baseline(unparseable)
        print(f"wrote {len(unparseable)} entr{'y' if len(unparseable)==1 else 'ies'} "
              f"to tools/verify_certificates_baseline.txt")
        return 0

    if errors:
        print(f"FAIL: {len(errors)} certificate problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK: every claimed certificate independently reverifies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
