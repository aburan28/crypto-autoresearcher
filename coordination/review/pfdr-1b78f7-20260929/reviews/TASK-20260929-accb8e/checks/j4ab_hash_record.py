"""J4(a)/(b) hash record (final review). sha256 of every file the analysis and merge
re-executions wrote to scratch, beside the archived file of the same name, compressed bytes
and (for .gz) decompressed bytes. Nothing is parsed or printed except digests; the analysis
outputs contain the A7 section by construction and are compared by hash only."""
import gzip, hashlib, json, os, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
S = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-accb8e"
RUNS = os.path.join(rl.WT, "experiments/EXP-PFDR-1b78f7/runs")
PAIRS = {
    "r15-out": "RUN-PFDR-1b78f7-analysis",
    "r16-out": "RUN-PFDR-1b78f7-stage-r",
    "merge-R11": "RUN-PFDR-1b78f7-census-m4/merged",
    "merge-R12": "RUN-PFDR-1b78f7-census-m5",
    "merge-R14": "RUN-PFDR-1b78f7-j0",
    "merge-R16": "RUN-PFDR-1b78f7-stage-r",
}


def h(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hz(p):
    return hashlib.sha256(gzip.open(p, "rb").read()).hexdigest()


out = {}
for sd, ad in PAIRS.items():
    for name in sorted(os.listdir(os.path.join(S, sd))):
        sp = os.path.join(S, sd, name)
        if os.path.islink(sp) or not os.path.isfile(sp):
            continue
        ap = os.path.join(RUNS, ad, name)
        ent = {"scratch": f"rv-accb8e/{sd}/{name}", "scratch_sha256": h(rl.opened(sp, "J4 hash record: sha256 only"))}
        if os.path.exists(ap):
            ent["archived"] = os.path.relpath(ap, rl.WT)
            ent["archived_sha256"] = h(rl.opened(ap, "J4 hash record: sha256 only (no content read)"))
            ent["bytes_equal"] = ent["scratch_sha256"] == ent["archived_sha256"]
            if name.endswith(".gz"):
                ent["decompressed_equal"] = hz(sp) == hz(ap)
        else:
            ent["archived"] = None
        out[f"{sd}/{name}"] = ent
json.dump(out, open(os.path.join(W, "checks/out/j4ab-reexec-hashes.json"), "w"), indent=1)
for k, v in out.items():
    print(k, "archived:", v.get("archived"), "bytes_equal:", v.get("bytes_equal"), "decompressed_equal:", v.get("decompressed_equal", "-"))
