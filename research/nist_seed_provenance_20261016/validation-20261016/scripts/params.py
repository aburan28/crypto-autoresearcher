#!/usr/bin/env python3
"""Published curve parameters from retrieved sources, cross-checked.

Sources (all retrieved 2026-10-16, see ../specs/):
  * `openssl ecparam -name <curve> -param_enc explicit -text -noout` (OpenSSL 3.0.13)
  * FIPS 186-2 Change Notice 1 excerpt (P-192..P-521: p, r=order, s=seed, c, b;
    B-163..B-571 seeds)
  * NIST SP 800-186 excerpt (P-224..P-521: p, n, a, b, Seed, c; B-233..B-571 seeds)
Writes ../out/params.json and prints every disagreement.
Written by the Validator (VAL-20261016-cd9156) from the public texts only.
"""
import json, re, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CURVES = [
    # label, openssl name, kind
    ("P-192", "prime192v1", "prime"),
    ("prime192v2", "prime192v2", "prime"),
    ("prime192v3", "prime192v3", "prime"),
    ("P-224", "secp224r1", "prime"),
    ("prime239v1", "prime239v1", "prime"),
    ("prime239v2", "prime239v2", "prime"),
    ("prime239v3", "prime239v3", "prime"),
    ("P-256", "prime256v1", "prime"),
    ("P-384", "secp384r1", "prime"),
    ("P-521", "secp521r1", "prime"),
    ("B-233", "sect233r1", "binary"),
    ("B-283", "sect283r1", "binary"),
    ("B-409", "sect409r1", "binary"),
    ("B-571", "sect571r1", "binary"),
]


def openssl_params(name):
    out = subprocess.run(["openssl", "ecparam", "-name", name, "-param_enc",
                          "explicit", "-text", "-noout"], capture_output=True,
                         text=True, check=True).stdout
    fields = {}
    key = None
    for line in out.splitlines():
        m = re.match(r"^(\w[\w \(\)-]*?):\s*(.*)$", line)
        if m and not line.startswith(" "):
            key = m.group(1).strip()
            rest = m.group(2).strip()
            fields[key] = rest
        elif key is not None:
            fields[key] = fields[key] + " " + line.strip()
    def hx(k):
        s = fields[k]
        m = re.search(r"\(0x([0-9a-fA-F]+)\)", s)
        if m:  # small values are printed as "1 (0x1)"
            return int(m.group(1), 16)
        return int(s.replace(":", "").replace(" ", ""), 16)
    res = {}
    for k_out, k_in in (("p", "Prime"), ("a", "A"), ("b", "B"), ("n", "Order"),
                        ("seed", "Seed"), ("poly", "Polynomial")):
        if k_in in fields:
            res[k_out] = hx(k_in)
    res["cofactor"] = int(re.match(r"\s*(\d+)", fields["Cofactor"]).group(1))
    return res


def parse_fips(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    res = {}
    blocks = re.split(r"\n\s*Curve (P-\d+)\s*\n", txt.split("## binary-curve seeds")[0])
    for i in range(1, len(blocks), 2):
        label, body = blocks[i], blocks[i + 1]
        vals, key = {}, None
        for line in body.splitlines():
            m = re.match(r"^\s*(p|r|s|c|b|Gx|Gy)=\s*(.*)$", line)
            if m:
                key = m.group(1)
                vals[key] = m.group(2)
            elif key and re.match(r"^\s+[0-9a-f\\ ]+$", line) and line.strip():
                vals[key] += " " + line.strip()
            elif not line.strip():
                key = key  # blank lines inside a block are harmless
        def dec(v):
            return int(re.sub(r"[^0-9]", "", v))
        def hx(v):
            return int(re.sub(r"[^0-9a-f]", "", v), 16)
        res[label] = {"p": dec(vals["p"]), "n": dec(vals["r"]), "seed": hx(vals["s"]),
                      "c": hx(vals["c"]), "b": hx(vals["b"])}
    seeds = re.findall(r"s=\s+([0-9a-f ]{40,})", txt.split("## binary-curve seeds")[1].split("##")[0])
    for label, s in zip(["B-163", "B-233", "B-283", "B-409", "B-571"], seeds):
        res[label] = {"seed": int(s.replace(" ", ""), 16)}
    return res


def parse_sp(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    res = {}
    main, binpart = txt.split("## binary seeds")
    parts = re.split(r"\n3\.2\.1\.\d\.\s+(P-\d+)\s*\n", main)
    for i in range(1, len(parts), 2):
        label, body = parts[i], parts[i + 1]
        vals, key = {}, None
        for line in body.splitlines():
            m = re.match(r"^(p|h|n|tr|a|b|Gx|Gy|Seed|c):\s*(.*)$", line)
            if m:
                key = m.group(1)
                vals[key] = m.group(2)
            elif key:
                vals[key] += " " + line.strip()
        def hexin(v):
            m = re.search(r"\(=0x([0-9a-f \\]+)\)", v)
            return int(re.sub(r"[^0-9a-f]", "", m.group(1)), 16)
        res[label] = {"p": hexin(vals["p"]), "n": hexin(vals["n"]), "a": hexin(vals["a"]),
                      "b": hexin(vals["b"]), "c": hexin(vals["c"]),
                      "seed": int(re.sub(r"[^0-9a-f]", "", vals["Seed"].split("0x", 1)[1]), 16)}
    seeds = re.findall(r"Seed:\s+0x([0-9a-f ]+)", binpart)
    for label, s in zip(["B-233", "B-283", "B-409", "B-571"], seeds):
        res[label] = {"seed": int(s.replace(" ", ""), 16)}
    return res


def main():
    fips = parse_fips(os.path.join(ROOT, "specs", "fips186-2_excerpt.txt"))
    sp = parse_sp(os.path.join(ROOT, "specs", "sp800186_params_excerpt.txt"))
    out, disagreements, agreements = {}, [], []
    for label, name, kind in CURVES:
        o = openssl_params(name)
        rec = {"label": label, "openssl_name": name, "kind": kind}
        for k, v in o.items():
            rec[k] = v
        for srcname, src in (("FIPS186-2", fips), ("SP800-186", sp)):
            if label in src:
                for k, v in src[label].items():
                    if k == "c":
                        rec.setdefault("c_published", {})[srcname] = v
                        continue
                    if k in o:
                        if o[k] != v:
                            disagreements.append((label, k, "openssl", srcname, hex(o[k]), hex(v)))
                        else:
                            agreements.append((label, k, srcname))
        if kind == "prime":
            assert rec["a"] == rec["p"] - 3, label
        out[label] = rec
    js = {k: {kk: (hex(vv) if isinstance(vv, int) and kk not in ("cofactor",) else vv)
              for kk, vv in v.items()} for k, v in out.items()}
    for k, v in out.items():
        if "c_published" in v:
            js[k]["c_published"] = {s: hex(c) for s, c in v["c_published"].items()}
    path = os.path.join(ROOT, "out", "params.json")
    with open(path, "w") as f:
        json.dump(js, f, indent=1, sort_keys=True)
    print("curves:", len(out))
    print("field agreements (openssl vs standard text):", len(agreements))
    for a in sorted(set((l, s) for l, k, s in agreements)):
        print("  agree", a[0], a[1], sorted(k for l, k, s in agreements if (l, s) == a))
    print("disagreements:", len(disagreements))
    for d in disagreements:
        print("  DISAGREE", d)
    for k, v in out.items():
        print(k, "seed", "%040x" % v["seed"], "p bits", v["p"].bit_length() if v["kind"] == "prime" else "-",
              "n bits", v["n"].bit_length())


if __name__ == "__main__":
    main()
