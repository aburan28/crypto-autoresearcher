#!/usr/bin/env python3
"""Parse the fetched SafeCurves HTML tables into per-curve cell lists.

Stdlib only. Input: retrieved-pages/safecurves-<page>.html. Output: JSON on
stdout mapping page -> table index -> curve -> list of cleaned cell strings.
"""
import html, json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ["field", "equation", "base", "rho", "twist", "disc", "index"]
CURVES = ["Anomalous", "M-221", "E-222", "NIST P-224", "Curve1174", "Curve25519",
          "BN(2,254)", "brainpoolP256t1", "ANSSI FRP256v1", "NIST P-256", "secp256k1",
          "E-382", "M-383", "Curve383187", "brainpoolP384t1", "NIST P-384",
          "Curve41417", "Ed448-Goldilocks", "M-511", "E-521"]

def clean(cell):
    cell = re.sub(r"<wbr\s*/?>", "", cell)
    cell = re.sub(r"<br\s*/?>", "", cell)
    cell = re.sub(r"<[^>]+>", "", cell)
    cell = html.unescape(cell)
    return re.sub(r"\s+", " ", cell).strip()

def parse(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    tables = re.findall(r"<table.*?</table>", src, flags=re.S)
    out = []
    for tb in tables:
        rows = {}
        for tr in re.findall(r"<tr.*?</tr>", tb, flags=re.S):
            cells = [clean(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S)]
            if cells and cells[0] in CURVES:
                rows[cells[0]] = cells[1:]
        out.append(rows)
    return out

def main():
    res = {}
    for pg in PAGES:
        p = os.path.join(HERE, "retrieved-pages", f"safecurves-{pg}.html")
        if os.path.exists(p):
            res[pg] = parse(p)
    json.dump(res, sys.stdout, indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
