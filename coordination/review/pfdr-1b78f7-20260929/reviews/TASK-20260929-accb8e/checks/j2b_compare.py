"""J2b (AFTER THE SEAL): compare my sealed J2a canonical sets, record by record in the
same normal form, with the producer's canonical files (R11 merged/, R12, R14, R16 run
roots), my lists with each merge-report.json, and check view-map.json /
view-map-stage-r.json against the archived files. Own comparator."""
import gzip, hashlib, json, os, sys, collections
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
sys.path.insert(0, os.path.join(W, "rederivation"))
import rl  # noqa
from common import RUNS, RUN, OUT, canon_bytes, sha256_bytes, key_of, sort_key, stair_key  # noqa

CH = os.path.join(W, "checks", "out")
os.makedirs(CH, exist_ok=True)


def load_gz(p, note):
    rl.opened(p, note)
    with gzip.open(p, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def diff_records(mine, theirs, keyf):
    res = {"mine": len(mine), "theirs": len(theirs), "equal_normal_form": canon_bytes(mine) == canon_bytes(theirs),
           "mine_sha": sha256_bytes(canon_bytes(mine)), "theirs_sha": sha256_bytes(canon_bytes(theirs))}
    if not res["equal_normal_form"]:
        km = [keyf(r) for r in mine]
        kt = [keyf(r) for r in theirs]
        res["same_key_sequence"] = km == kt
        res["same_key_set"] = sorted(map(str, km)) == sorted(map(str, kt))
        dm = collections.Counter()
        first = []
        tm = {str(keyf(r)): r for r in theirs}
        for r in mine:
            t = tm.get(str(keyf(r)))
            if t is None:
                dm["missing_in_theirs"] += 1
                continue
            if json.dumps(r, sort_keys=True) != json.dumps(t, sort_keys=True):
                dm["differs"] += 1
                ks = sorted(set(r) | set(t))
                dk = [k for k in ks if r.get(k) != t.get(k)]
                if len(first) < 5:
                    first.append({"key": str(keyf(r)), "differing_fields": dk})
                for k in dk:
                    dm[f"field:{k}"] += 1
        res["differences"] = dict(dm)
        res["examples"] = first
        # order check: is theirs sorted by the M-5 rule?
    return res


def main():
    out = {}
    j2a = json.load(open(os.path.join(OUT, "j2a-report.json")))
    for lab, where in [("R11", "merged"), ("R12", ""), ("R14", ""), ("R16", "")]:
        rd = os.path.join(RUNS, RUN[lab], where) if where else os.path.join(RUNS, RUN[lab])
        mine_rows = load_gz(os.path.join(OUT, f"canonical-{lab}-rows.jsonl.gz"), f"J2b: my sealed canonical {lab} rows")
        mine_st = load_gz(os.path.join(OUT, f"canonical-{lab}-staircase.jsonl.gz"), f"J2b: my sealed canonical {lab} staircase")
        th_rows = load_gz(os.path.join(rd, "rows.jsonl.gz"), f"J2b: producer canonical {lab} rows (blind_from, after seal)")
        th_st = load_gz(os.path.join(rd, "staircase.jsonl.gz"), f"J2b: producer canonical {lab} staircase (blind_from, after seal)")
        r = {"rows": diff_records(mine_rows, th_rows, key_of),
             "staircase": diff_records(mine_st, th_st, lambda s: (stair_key(s), s["class"]))}
        r["theirs_rows_sorted_by_M5"] = [sort_key(x) for x in th_rows] == sorted(sort_key(x) for x in th_rows)
        mr_p = os.path.join(rd, "merge-report.json")
        mr = json.load(open(rl.opened(mr_p, f"J2b: producer merge-report {lab} (blind_from, after seal)")))
        r["merge_report_top_keys"] = sorted(mr.keys())
        out[lab] = r
    with open(os.path.join(CH, "j2b-compare.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for lab, r in out.items():
        print(lab, "rows equal:", r["rows"]["equal_normal_form"], r["rows"]["mine"], r["rows"]["theirs"],
              "| stair equal:", r["staircase"]["equal_normal_form"], r["staircase"]["mine"], r["staircase"]["theirs"],
              "| sorted:", r["theirs_rows_sorted_by_M5"], "| diffs:", r["rows"].get("differences"), r["staircase"].get("differences"))


if __name__ == "__main__":
    main()
