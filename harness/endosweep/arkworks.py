"""Curves of the arkworks-rs/curves workspace, as a std-curves-format category.

The std-curves database (``corpus.py``) predates most zero-knowledge curves:
it has BLS12-377/381, BN254, Pallas/Vesta and JubJub but not MNT4/MNT6 at 298
and 753 bits, CP6-782, BW6-761/767, Grumpkin, secq256k1, Baby JubJub or the
Edwards curves built over the other fields.  The arkworks crates define all of
them in Rust source, and this module turns that source into entries the
corpus scanner reads unchanged:

* every file is fetched at one pinned commit of
  https://github.com/arkworks-rs/curves (``RAW`` below) and its sha256
  recorded;
* the base field ``Fq`` and scalar field ``Fr`` moduli come from each crate's
  ``#[modulus = "..."]`` attribute, following ``pub use ark_x::{Fr as Fq}``
  re-exports across crates;
* the curve is the G1 ``SWCurveConfig`` (``COEFF_A``, ``COEFF_B``) or the
  ``TECurveConfig`` (``COEFF_A``, ``COEFF_D``) with its ``COFACTOR`` limbs and
  generator; the group order is ``COFACTOR * |Fr|``.

Nothing here is trusted beyond parsing: the scanner verifies every entry from
its constants (prime n, Hasse interval, a point of order divisible by n killed
by h*n), and :func:`check_entry` additionally checks that the declared
generator is on the curve and killed by h*n.  An entry whose source cannot be
parsed is reported with the reason, never guessed.

    python -m harness.endosweep.arkworks --commit e2d16a27e2cfa9f972ae9772df827a22730011b4 \\
        --out-dir research/endosweep_curves_20261006/arkworks
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess

REPO = "arkworks-rs/curves"
RAW = "https://raw.githubusercontent.com/{repo}/{commit}/{crate}/{path}"

# every curve crate of the workspace (its Cargo.toml members), in workspace order
CRATES = [
    "bls12_377", "ed_on_bls12_377", "bw6_761", "ed_on_bw6_761", "bw6_767", "cp6_782", "ed_on_cp6_782",
    "bls12_381", "ed_on_bls12_381", "ed_on_bls12_381_bandersnatch", "bn254", "ed_on_bn254", "grumpkin",
    "mnt4_298", "mnt6_298", "ed_on_mnt4_298", "mnt4_753", "mnt6_753", "ed_on_mnt4_753",
    "pallas", "vesta", "secp256k1", "secp256r1", "secp384r1", "secq256k1", "curve25519", "ed25519",
]
FILES = ["src/fields/fq.rs", "src/fields/fr.rs", "src/curves/mod.rs", "src/curves/g1.rs", "src/lib.rs"]


def fetch(commit: str, cache_dir: str) -> dict:
    """Download every crate file at ``commit`` (missing files are recorded as such)."""
    out: dict = {}
    for crate in CRATES:
        for path in FILES:
            url = RAW.format(repo=REPO, commit=commit, crate=crate, path=path)
            local = os.path.join(cache_dir, commit, crate, path)
            if not os.path.exists(local):
                r = subprocess.run(["curl", "-sS", "-w", "%{http_code}", "-o", "-", url], capture_output=True)
                body, code = r.stdout[:-3], r.stdout[-3:].decode(errors="replace")
                if code != "200":
                    continue
                os.makedirs(os.path.dirname(local), exist_ok=True)
                with open(local, "wb") as f:
                    f.write(body)
            with open(local, "rb") as f:
                data = f.read()
            out[(crate, path)] = {"text": data.decode(), "url": url, "sha256": hashlib.sha256(data).hexdigest()}
    return out


_MODULUS = re.compile(r'#\[modulus\s*=\s*"(\d+)"\]')
_REEXPORT = re.compile(r"pub use ark_(\w+)::\{\s*(Fq|Fr)\b(?:\s+as\s+(Fq|Fr))?")
_GLOB_REEXPORT = re.compile(r"pub use ark_(\w+)::\*;")


def _alias(files: dict, crate: str) -> str:
    """``ed_on_bw6_761`` is ``pub use ark_ed_on_cp6_782::*``: follow such crates."""
    lib = files.get((crate, "src/lib.rs"), {}).get("text", "")
    m = _GLOB_REEXPORT.search(lib)
    if m and (crate, "src/curves/mod.rs") not in files:
        return m.group(1)
    return crate


def field_modulus(files: dict, crate: str, which: str, _depth: int = 0) -> int:
    """The modulus of ``crate``'s ``fq`` or ``fr``, following re-exports."""
    if _depth > 4:
        raise ValueError("re-export chain too long")
    crate = _alias(files, crate)
    text = files.get((crate, f"src/fields/{which}.rs"), {}).get("text")
    if text is None:
        raise ValueError(f"{crate}: no src/fields/{which}.rs")
    m = _MODULUS.search(text)
    if m:
        return int(m.group(1))
    m = _REEXPORT.search(text)
    if m:
        return field_modulus(files, m.group(1), m.group(2).lower(), _depth + 1)
    raise ValueError(f"{crate}: no modulus or re-export in src/fields/{which}.rs")


def _block(text: str, header: re.Pattern) -> str | None:
    """The body of the first ``impl ... {`` block matching ``header``."""
    m = header.search(text)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[m.end():i - 1]


def _expr(expr: str, p: int) -> int:
    """A field-element expression of the curve sources, reduced mod p."""
    e = " ".join(expr.split())
    m = re.fullmatch(r'MontFp!\(\s*"(-?\d+)"\s*\)', e)
    if m:
        return int(m.group(1)) % p
    table = {"Fq::ZERO": 0, "Fq::ONE": 1, "-Fq::ONE": -1, "Self::BaseField::ZERO": 0, "Self::BaseField::ONE": 1}
    if e in table:
        return table[e] % p
    raise ValueError(f"unparsed field expression {e!r}")


def _const(block: str, name: str, p: int) -> int:
    m = re.search(rf"const\s+{name}\s*:\s*[\w:]+\s*=\s*(.*?);", block, re.S)
    if not m:
        raise ValueError(f"no const {name}")
    return _expr(m.group(1), p)


def _cofactor(text: str) -> int:
    m = re.search(r"const\s+COFACTOR\s*:\s*&'static\s*\[u64\]\s*=\s*&\[(.*?)\];", text, re.S)
    if not m:
        raise ValueError("no COFACTOR")
    limbs = [x.strip() for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
    value = 0
    for i, limb in enumerate(limbs):
        limb = limb.replace("_", "")
        value |= (int(limb, 16) if limb.lower().startswith("0x") else int(limb)) << (64 * i)
    return value


def _generator(text: str, block: str, p: int) -> tuple[int, int] | None:
    m = re.search(r"const\s+GENERATOR\s*:\s*\w+\s*=\s*\w+::new_unchecked\(\s*(\w+)\s*,\s*(\w+)\s*\)", block)
    if not m:
        return None
    coords = []
    for name in m.groups():
        mm = re.search(rf"pub const\s+{name}\s*:\s*Fq\s*=\s*(.*?);", text, re.S)
        if not mm:
            return None
        coords.append(_expr(mm.group(1), p))
    return coords[0], coords[1]


def extract(files: dict, crate: str, commit: str) -> dict:
    """One std-curves-format entry (or one with ``"unparsed"`` set)."""
    entry: dict = {"name": crate, "category": "arkworks", "sources": [], "characteristics": {}}
    try:
        src_crate = _alias(files, crate)
        if src_crate != crate:
            entry["alias_of"] = src_crate
        path = "src/curves/g1.rs" if (src_crate, "src/curves/g1.rs") in files else "src/curves/mod.rs"
        text = files[(src_crate, path)]["text"]
        p = field_modulus(files, src_crate, "fq")
        n = field_modulus(files, src_crate, "fr")
        sw = _block(text, re.compile(r"impl\s+SWCurveConfig\s+for\s+\w+\s*\{"))
        te = _block(text, re.compile(r"impl\s+TECurveConfig\s+for\s+\w+\s*\{"))
        # a crate may carry both (BLS12-377's G1 has a twisted Edwards model for
        # faster arithmetic); the short Weierstrass one is the curve's definition
        if sw is not None:
            form, a, other = "Weierstrass", _const(sw, "COEFF_A", p), ("b", _const(sw, "COEFF_B", p))
            gen = _generator(text, sw, p)
        elif te is not None:
            form, a, other = "TwistedEdwards", _const(te, "COEFF_A", p), ("d", _const(te, "COEFF_D", p))
            gen = _generator(text, te, p)
        else:
            raise ValueError("no SWCurveConfig or TECurveConfig")
        h = _cofactor(text)
        entry.update({
            "field": {"type": "Prime", "p": hex(p), "bits": p.bit_length()},
            "form": form,
            "params": {"a": {"raw": hex(a)}, other[0]: {"raw": hex(other[1])}},
            "order": hex(n),
            "cofactor": hex(h),
        })
        if gen is not None:
            entry["generator"] = {"x": {"raw": hex(gen[0])}, "y": {"raw": hex(gen[1])}}
        for c, f in sorted(files):
            if c in (crate, src_crate) and f in (path, "src/fields/fq.rs", "src/fields/fr.rs", "src/lib.rs"):
                entry["sources"].append({"name": f"{REPO}@{commit} {c}/{f}", "url": files[(c, f)]["url"],
                                         "sha256": files[(c, f)]["sha256"]})
    except Exception as e:  # noqa: BLE001 - the reason is the record
        entry["unparsed"] = f"{type(e).__name__}: {e}"
        entry["field"] = {"type": "Prime", "bits": 0}
    return entry


def check_entry(entry: dict) -> str:
    """The declared generator is on the curve and h*n kills it (or why not)."""
    from .targets import _e_add, _mul, _w_add
    if "unparsed" in entry or "generator" not in entry:
        return "no generator to check"
    p = int(entry["field"]["p"], 16)
    n, h = int(entry["order"], 16), int(entry["cofactor"], 16)
    x, y = int(entry["generator"]["x"]["raw"], 16), int(entry["generator"]["y"]["raw"], 16)
    a = int(entry["params"]["a"]["raw"], 16)
    if entry["form"] == "Weierstrass":
        b = int(entry["params"]["b"]["raw"], 16)
        if (y * y - (x ** 3 + a * x + b)) % p:
            return "generator NOT on the curve"
        R = _mul(lambda P, Q: _w_add(p, a, P, Q), None, h * n, (x, y))
        return "generator on the curve, killed by h*n" if R is None else "generator NOT killed by h*n"
    d = int(entry["params"]["d"]["raw"], 16)
    if (a * x * x + y * y - 1 - d * x * x * y * y) % p:
        return "generator NOT on the curve"
    R = _mul(lambda P, Q: _e_add(p, a, d, P, Q), (0, 1), h * n, (x, y))
    return "generator on the curve, killed by h*n" if R == (0, 1) else "generator NOT killed by h*n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="arkworks-rs/curves as a std-curves-format category")
    ap.add_argument("--commit", required=True)
    ap.add_argument("--cache-dir", default=os.path.join(os.path.expanduser("~"), ".cache", "endosweep-arkworks"))
    ap.add_argument("--out-dir", required=True, help="writes <out-dir>/curves.json")
    args = ap.parse_args(argv)
    files = fetch(args.commit, args.cache_dir)
    entries = []
    for crate in CRATES:
        e = extract(files, crate, args.commit)
        e["generator_check"] = check_entry(e)
        entries.append(e)
        print(f"{crate:32s} {e.get('form', '-'):15s} {e['field'].get('bits', 0):4d} bits  "
              f"{e.get('unparsed') or e['generator_check']}")
    os.makedirs(args.out_dir, exist_ok=True)
    doc = {"name": "arkworks", "desc": f"G1 of every curve crate of {REPO} at commit {args.commit}, "
                                       "extracted by harness/endosweep/arkworks.py",
           "commit": args.commit, "curves": entries}
    with open(os.path.join(args.out_dir, "curves.json"), "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    bad = [e["name"] for e in entries if "unparsed" in e or "NOT" in e.get("generator_check", "")]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
