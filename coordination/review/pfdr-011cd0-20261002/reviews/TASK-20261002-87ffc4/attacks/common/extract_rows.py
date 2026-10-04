"""Stream the archived canonical rows of R12 (table) and R13 (search) and write a compact
per-instance extract (one JSON line per instance) for the red-team J4/J8/PTM attacks.

Reads (streamed, line by line, never loaded whole): <WT>/experiments/EXP-PFDR-011cd0/runs/
RUN-PFDR-011cd0-table/rows.jsonl.gz and RUN-PFDR-011cd0-search/rows.jsonl.gz (the merged canonical
rows the R15/R16 view maps bind). Every arm is read (the red team is not blind to the producer's
outputs; card inputs). Fields kept: instance key, status, N, log2N, fb_size, U, table
formally_distinct_tails, and per class the harvester's in-process counts (G-REL-gated):
relations_nonformal, relations_distinct, pairs_nonformal, pairs_raw, informative_rank, R_star,
multiplicity_histogram; SS also its at_X_fix block. No floor or A7 quantity exists in these rows'
kept fields, and none is computed.

Command: nice -n 19 $PY attacks/common/extract_rows.py --out <scratch>/extract.jsonl.gz
"""
import argparse
import gzip
import hashlib
import json
import os

WT = os.environ.get("RT_WT", "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/"
                    "wt-pfdr011cd0-5753edf2e")
RUNS = os.path.join(WT, "experiments", "EXP-PFDR-011cd0", "runs")


def cls_block(st):
    return {"n": st.get("relations_nonformal"), "raw": st.get("relations_distinct"),
            "pairs": st.get("pairs_nonformal"), "pairs_raw": st.get("pairs_raw"),
            "irank": st.get("informative_rank"), "R_star": st.get("R_star"),
            "hist": st.get("multiplicity_histogram"), "rows_nonformal": st.get("rows_nonformal")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    n = 0
    shas = {}
    with gzip.open(a.out, "wt") as fo:
        for run in ("RUN-PFDR-011cd0-table", "RUN-PFDR-011cd0-search"):
            path = os.path.join(RUNS, run, "rows.jsonl.gz")
            hsh = hashlib.sha256(open(path, "rb").read()).hexdigest()
            shas[run] = hsh
            with gzip.open(path, "rt") as fi:
                for line in fi:
                    r = json.loads(line)
                    h = r.get("harvest") or {}
                    rec = {"run": run, "bits": r["bits"], "curve": r["curve"], "m": int(r["method"][4:]) if
                           r.get("method", "").startswith("ic_m") else r.get("m"),
                           "arm": r.get("arm"), "mode": r.get("mode"), "status": r.get("status"),
                           "N": r.get("N"), "log2N": r.get("log2N"), "s": r.get("fb_size"),
                           "fb": r.get("fb"), "U": h.get("U"), "table_arity": r.get("table_arity")}
                    if h:
                        rec["Ep"] = (h.get("table") or {}).get("formally_distinct_tails")
                        rec["entries"] = (h.get("table") or {}).get("entries")
                        rec["formal_basis_rank"] = h.get("formal_basis_rank")
                        for c in ("TT", "TB", "SS"):
                            if c in h:
                                rec[c] = cls_block(h[c]["at_stop"])
                        xf = (h.get("SS") or {}).get("at_X_fix")
                        if xf:
                            rec["SSx"] = {"n": xf.get("relations_nonformal"), "raw": xf.get("relations_distinct"),
                                          "pairs": xf.get("pairs_nonformal"), "pairs_raw": xf.get("pairs_raw"),
                                          "X": xf.get("formally_distinct_encodings"), "X_fix": xf.get("X_fix"),
                                          "censored": xf.get("censored"), "R_star": xf.get("R_star"),
                                          "hist": xf.get("multiplicity_histogram")}
                        rec["fb_params_planted"] = (r.get("fb_params") or {}).get("planted_relations") is not None
                    fo.write(json.dumps(rec, separators=(",", ":")) + "\n")
                    n += 1
    out_sha = hashlib.sha256(open(a.out, "rb").read()).hexdigest()
    print(json.dumps({"instances": n, "input_sha256": shas, "out": a.out, "out_sha256": out_sha}))


if __name__ == "__main__":
    main()
