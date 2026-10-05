"""msparse.py -- my own parser of msolve .ms files written by boolsys.write_msolve (variable line, '2', comma-separated polynomials)."""
import re
def parse_ms(path):
    lines = open(path).read().split("\n")
    names = lines[0].split(",")
    assert lines[1].strip() == "2", "characteristic line"
    body = "\n".join(lines[2:]).strip()
    polys = [p.strip() for p in body.split(",\n") if p.strip()]
    idx = {v: i for i, v in enumerate(names)}
    eqs, field = [], []
    for p in polys:
        m = re.fullmatch(r"(\S+)\^2\+(\S+)", p)
        if m and m[1] == m[2]:
            field.append(m[1]); continue
        masks = []
        for t in p.split("+"):
            if t == "1": masks.append(0); continue
            mask = 0
            for v in t.split("*"):
                mask |= 1 << idx[v]
            masks.append(mask)
        assert len(set(masks)) == len(masks)
        eqs.append(sorted(masks))
    return names, eqs, field
