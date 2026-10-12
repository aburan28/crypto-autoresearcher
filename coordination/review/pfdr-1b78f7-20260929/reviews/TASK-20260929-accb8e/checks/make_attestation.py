"""Build attestation.yaml (review_attestation) from checks/read-log.txt.

sources_read: every path in the read log, first occurrence only, in chronological order to
the minute (the log's first column truncated to HH:MM), ties broken by the log's sequence
number. This places the retrospective entries 1438-1450 (minute-precision times) at their
recorded minute rather than at their logging position. Two log entries whose path column is
not a plain path are mapped: seq 5 (a listing of two directories) to the two directory paths,
seq 11 (git metadata of the detached worktree) to '.git'. Paths of the detached worktree
(WT) and of the shared tree (SHARED) are repo-relative; this task's own files are
repo-relative under its write scope; scratch paths are absolute. The tree each entry was read
from, its time and what was read are in the log. The blind_from leak computation mirrors
tools/check_review_independence.py (r == b or r.startswith(b.rstrip('/') + '/'))."""
import hashlib, os, sys
import yaml

W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
SHARED = "/home/user/crypto-autoresearcher"
REL_W = os.path.relpath(W, SHARED)
LOG = os.path.join(W, "checks", "read-log.txt")
CARD = os.path.join(SHARED, "ledger/handoffs/TASK-20260929-accb8e.yaml")
SEALED = os.path.join(W, "rederivation", "sealed-section.yaml")
SEALED_SHA = "9b81b04911f9307062c80bb335557ea4d858541f93940e867b300131ad4234da"

EXCLUDED = [
    "coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-f29c96/",
    "coordination/review/pfdr-7c8bf2-20260929/",
    "ledger/evidence/EV-PFDR-cf6ee5.yaml",
    "ledger/decisions/DEC-20260929-1b779a.yaml",
    "experiments/EXP-PFDR-7c8bf2/analysis.md",
    "scratchpad/89c123/",
    "coordination/bus/",
]


def hits(r, b):
    return r == b or r.startswith(b.rstrip("/") + "/")


def main():
    sha = hashlib.sha256(open(SEALED, "rb").read()).hexdigest()
    assert sha == SEALED_SHA, "sealed file hash changed"
    entries, seal_seen, pre_seal_seqs = [], False, []
    for line in open(LOG):
        if line.startswith("# ==== SEAL ===="):
            seal_seen = True
            continue
        if line.startswith("#") or not line.strip():
            continue
        t, seq, loc, path, note = (line.rstrip("\n").split("\t") + [""])[:5]
        seq = int(seq)
        if not seal_seen:
            pre_seal_seqs.append(seq)
        if seq == 5:
            paths = ["coordination/review/pfdr-1b78f7-20260929/",
                     "coordination/review/pfdr-1b78f7-20260929/launch-facts/"]
        elif seq == 11:
            paths = [".git"]
        else:
            paths = [path]
        for p in paths:
            entries.append((t[:16], seq, loc, p))
    order = sorted(entries, key=lambda e: (e[0], e[1]))
    seen, sources = set(), []
    for _, seq, loc, p in order:
        if p not in seen:
            seen.add(p)
            sources.append(p)
    card = yaml.safe_load(open(CARD))
    # the card's review plan: find blind_rederivation wherever it sits
    def find(o, key):
        if isinstance(o, dict):
            if key in o:
                return o[key]
            for v in o.values():
                r = find(v, key)
                if r is not None:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = find(v, key)
                if r is not None:
                    return r
        return None
    br = find(card, "blind_rederivation")
    blind_from = [str(b).strip() for b in br["blind_from"]]
    leaked = sorted({b for b in blind_from for r in sources if hits(r, b)})
    pre_seal_paths = {e[3] for e in entries if e[1] in set(pre_seal_seqs)}
    pre_leak = sorted({b for b in blind_from for r in pre_seal_paths if hits(r, b)})
    excl = sorted({x for x in EXCLUDED for r in sources if hits(r, x) or ("/" + x) in r})
    assert not pre_leak, pre_leak
    assert not excl, excl
    print("entries", len(entries), "unique paths", len(sources), "pre-seal entries", len(pre_seal_seqs),
          "blind_from entries", len(blind_from), "read after the seal", len(leaked), "pre-seal leaks", len(pre_leak),
          "excluded hits", len(excl))
    att = {
        "review_attestation": {
            "task_id": "TASK-20260929-accb8e",
            "reviewer": "validator-breakthrough (review-breakthrough, effort max); independent subagent session",
            "experiment_id": "EXP-PFDR-1b78f7",
            "object_under_review_commit": "a32e708088c16b46686ea19afaab72910a42d75f",
            "joints_owned": ["J1", "J2", "J3", "J4", "J5"],
            "verdicts": {"J1": "holds", "J2": "holds", "J3": "holds", "J4": "holds", "J5": "breaks"},
            "read_sibling_reports": False,
            "blind_from_respected": True,
            "blind_from_respected_meaning": (
                "True in RV-2's sense, the one this card's J3 cites: no path in the plan's "
                "blind_rederivation.blind_from was opened before the seal at 2026-09-29T08:02:39Z "
                f"({len(pre_seal_seqs)} read-log entries precede the seal line; 0 hit blind_from). It is NOT "
                "true in the template's literal sense (no blind_from path read at all). "
                f"{len(leaked)} blind_from entries were read AFTER the seal, for J1, J2b, the J3 "
                "comparison and J4, as PD-2 declares. They are listed below and inside sources_read, "
                "unsplit, so tools/check_review_independence.py reports them."),
            "sealed_at": "2026-09-29T08:02:39Z",
            "sealed_artifact": f"{REL_W}/rederivation/sealed-section.yaml",
            "sealed_artifact_sha256": SEALED_SHA,
            "read_log": f"{REL_W}/checks/read-log.txt",
            "blind_from_entries_read_after_the_seal": leaked,
            "expected_independence_checker_output": (
                "Per PD-2, exactly one problem from this attestation: the line reporting that re-deriver "
                "TASK-20260929-accb8e read the blind_from paths listed above. The checker was not run "
                "by this task (not among RV-7's permitted computations); its leak rule was mirrored in "
                "checks/make_attestation.py."),
            "not_read": [
                "coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-f29c96/ (the red team; never opened or listed)",
                "the red team's launch facts (launch-facts/TASK-20260929-f29c96.yaml; name seen in a listing, never opened)",
                "a harness task-output file announced near the end of this session as 'Red-team EXP-PFDR-1b78f7 census' (never opened)",
                "the parent-session transcript path offered after a context compaction (never opened)",
                "every read_scope_excludes path of the card; coordination/bus/; any PR text or comment; any commit message after a32e70808",
            ],
            "sources_read_rule": (
                "Every path in checks/read-log.txt, first occurrence only, in chronological order to the "
                "minute with ties broken by log sequence. Detached-worktree and shared-tree paths are "
                "repo-relative (the log records which tree), this task's own files are repo-relative under "
                "its write scope, and scratch paths are absolute. Log seq 5 (a listing) maps to its two "
                "directories and seq 11 (worktree git metadata) to .git. The runtime also injected CLAUDE.md "
                "and /home/user/cairn/CLAUDE.md as session context; neither was opened by a tool call. "
                "Self-checks made after this list was built (parsing attestation.yaml and "
                "validation-report.yaml back) are logged in the read log after it."),
            "sources_read_count": len(sources),
            "sources_read": sources,
        }
    }
    out = os.path.join(W, "attestation.yaml")
    with open(out, "w") as f:
        f.write("# review_attestation -- TASK-20260929-accb8e. Built by checks/make_attestation.py from checks/read-log.txt.\n")
        yaml.safe_dump(att, f, sort_keys=False, width=100, allow_unicode=False, default_flow_style=False)
    back = yaml.safe_load(open(out))["review_attestation"]
    assert back["sources_read"] == sources and back["verdicts"]["J5"] == "breaks" and back["blind_from_respected"] is True
    assert back["read_sibling_reports"] is False and back["sealed_artifact_sha256"] == SEALED_SHA
    print("written", out, "sha256", hashlib.sha256(open(out, "rb").read()).hexdigest())
    print("leaked blind_from entries:")
    for b in leaked:
        print("  ", b)


if __name__ == "__main__":
    main()
