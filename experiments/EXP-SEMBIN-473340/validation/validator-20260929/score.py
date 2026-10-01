"""Validator's independent scorer for EXP-SEMBIN-473340 (VAL-20260929-sembin473340).

Implements specification.yaml scoring_rule verbatim, from results.json alone:
  * censoring: "None" is CENSORED, ranked above every integer; median of 25 is
    the 13th order statistic; median of 10 is the mean of the 5th and 6th; a
    median touching a CENSORED order statistic is CENSORED.
  * P1_c, P2_c, P3_c per-cell conditions and aggregation (holds / fails /
    indeterminate), never pooled across conventions or across P.
Also: C1 against the MEASUREMENT1 markdown table itself (parsed from
research/FFD_SEMAEV_MEASUREMENT1.md, NOT remeasure.PUBLISHED), C3 counts,
C4 scorer self-test on the legacy column, and secondary descriptive
quantities.

usage: python3 score.py RESULTS.json [OUT.json]
"""
import sys, json, re, os

CENS = "CENSORED"
CELLS = [(n, npr) for n in (4, 5, 6, 7) for npr in (3, 4)]
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))


def expand(dist):
    """dist {'2': 9, '3': 1, 'None': k} -> sorted list with CENSORED last."""
    xs = []
    for k, v in dist.items():
        val = CENS if k == "None" else int(k)
        xs += [val] * v
    return sorted(xs, key=lambda x: (x == CENS, 0 if x == CENS else x))


def cmedian(dist):
    xs = expand(dist)
    L = len(xs)
    if L == 0:
        raise ValueError("empty distribution")
    if L % 2 == 1:
        return xs[L // 2]
    a, b = xs[L // 2 - 1], xs[L // 2]
    if a == CENS or b == CENS:
        return CENS
    return (a + b) / 2


def aggregate(conds):
    vals = [v for (_, v) in conds]
    if any(v is False for v in vals):
        return "fails"
    if any(v is None for v in vals):
        return "indeterminate"
    return "holds"


def score(cells, conv):
    med = {}
    for (n, npr), row in cells.items():
        med[(n, npr)] = (cmedian(row[conv]["semaev"]), cmedian(row[conv]["null"]))
    p1 = [((n, npr), (m[0] != CENS and m[0] == 2)) for (n, npr), m in sorted(med.items())]
    p2 = []
    for (n, npr), (s, u) in sorted(med.items()):
        if (n, npr) == (7, 3):
            continue
        if s == CENS:
            v = None                       # indeterminate
        elif u == CENS:
            v = True
        else:
            v = (u - s) >= 1
        p2.append(((n, npr), v))
    p3 = []
    for n in (4, 5, 6, 7):
        a, b = med[(n, 3)][1], med[(n, 4)][1]
        if a != CENS and b != CENS:
            v = b > a
        elif b == CENS and a != CENS:
            v = True
        elif a == CENS and b != CENS:
            v = False
        else:
            v = None
        p3.append((n, v))
    return med, {"P1": (aggregate(p1), p1), "P2": (aggregate(p2), p2), "P3": (aggregate(p3), p3)}


def parse_published():
    """Parse the section-2 table of research/FFD_SEMAEV_MEASUREMENT1.md."""
    txt = open(os.path.join(ROOT, "research", "FFD_SEMAEV_MEASUREMENT1.md")).read()
    sec = txt.split("## 2. Result", 1)[1].split("## 3.", 1)[0]
    pub = {}
    for line in sec.splitlines():
        m = re.match(r"\|\s*n=(\d+), n'=(\d+)\s*\|\s*(\d+)\s*\|\s*(\{[^}]*\})\s*\|\s*(\{[^}]*\})\s*\|\s*(\S+)\s*\|", line)
        if m:
            n, npr = int(m.group(1)), int(m.group(2))
            to = lambda s: {str(int(k)): int(v) for k, v in re.findall(r"(\d+):\s*(\d+)", s)}
            pub[(n, npr)] = dict(N=int(m.group(3)), semaev=to(m.group(4)), null=to(m.group(5)), deficit=m.group(6))
    return pub


def main():
    res = json.load(open(sys.argv[1]))
    out = {}
    cells = {}
    dup = {}
    for r in res["cells"]:
        key = (r["n"], r["nprime"])
        dup[key] = dup.get(key, 0) + 1
        cells[key] = r
    # C3
    c3 = dict(cells_present=sorted(map(list, cells)), each_declared_cell_once=all(dup.get(c, 0) == 1 for c in CELLS) and len(dup) == 8,
              counts={})
    ok = c3["each_declared_cell_once"]
    for c in CELLS:
        for conv in ("reduced", "formal", "legacy"):
            s = sum(cells[c][conv]["semaev"].values()); u = sum(cells[c][conv]["null"].values())
            c3["counts"][f"{c}/{conv}"] = [s, u]
            ok = ok and s == 10 and u == 25
    c3["pass"] = ok
    out["C3"] = c3
    # C1 against the markdown
    pub = parse_published()
    c1 = dict(parsed_cells=len(pub), per_cell={})
    allok = len(pub) == 8
    for c in CELLS:
        p = pub[c]
        same = (cells[c]["legacy"]["semaev"] == p["semaev"] and cells[c]["legacy"]["null"] == p["null"])
        c1["per_cell"][str(c)] = dict(published=dict(semaev=p["semaev"], null=p["null"], deficit=p["deficit"]),
                                      legacy=dict(semaev=cells[c]["legacy"]["semaev"], null=cells[c]["legacy"]["null"]),
                                      match=same, runner_flag=cells[c]["legacy_reproduces_published"])
        allok = allok and same
    c1["pass"] = allok and res["control_C1_legacy_reproduces_all"] is True
    c1["runner_control_C1_legacy_reproduces_all"] = res["control_C1_legacy_reproduces_all"]
    out["C1"] = c1
    # C4 + scoring
    scored = {}
    for conv in ("legacy", "reduced", "formal"):
        med, sc = score(cells, conv)
        scored[conv] = dict(
            medians={str(k): dict(semaev=v[0], null=v[1],
                                  runner_semaev_median=cells[k][conv]["semaev_median"],
                                  runner_null_median=cells[k][conv]["null_median"],
                                  deficit=(None if CENS in v else v[1] - v[0])) for k, v in sorted(med.items())},
            outcomes={P: dict(verdict=sc[P][0], conditions=[[str(k), v] for k, v in sc[P][1]]) for P in sc},
            semaev_draws_not_2={str(k): sum(v for kk, v in cells[k][conv]["semaev"].items() if kk != "2") for k in CELLS},
            any_dff_1_or_None={str(k): {kind: {kk: v for kk, v in cells[k][conv][kind].items() if kk in ("1", "None")} for kind in ("semaev", "null")} for k in CELLS},
        )
    out["C4"] = dict(legacy_outcomes={P: scored["legacy"]["outcomes"][P]["verdict"] for P in ("P1", "P2", "P3")})
    out["C4"]["pass"] = all(v == "holds" for v in out["C4"]["legacy_outcomes"].values())
    out["scored"] = scored
    out["six_outcomes"] = {f"{P}_{conv}": scored[conv]["outcomes"][P]["verdict"] for conv in ("reduced", "formal") for P in ("P1", "P2", "P3")}
    s = json.dumps(out, indent=1, default=str)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(s)
    print(json.dumps(dict(C1=c1["pass"], C3=c3["pass"], C4=out["C4"], six=out["six_outcomes"]), indent=1))


if __name__ == "__main__":
    main()
