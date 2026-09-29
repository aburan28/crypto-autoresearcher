"""J4(b) follow-up (final review): R16 raw-result.json from my merge re-execution (no
--post-command, PDV-2) differs in bytes from the archived one. Report ONLY the key paths
that differ or exist on one side, never a value (the file may carry analysis output)."""
import json, os, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
S = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rv-accb8e/merge-R16/raw-result.json"
A = os.path.join(rl.WT, "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-stage-r/raw-result.json")
a = json.load(open(rl.opened(A, "J4(b) follow-up: key paths that differ from my merge re-execution (no value printed)")))
s = json.load(open(rl.opened(S, "J4(b) follow-up: key-path diff (no value printed)")))
only_a, only_s, differ = [], [], []


def walk(x, y, p):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            q = f"{p}.{k}" if p else str(k)
            if k not in y:
                only_a.append(q)
            elif k not in x:
                only_s.append(q)
            else:
                walk(x[k], y[k], q)
    elif x != y:
        differ.append(p + (" (list)" if isinstance(x, list) else ""))


walk(a, s, "")
res = {"only_in_archived": only_a, "only_in_reexecution": only_s, "differing_paths": differ}
json.dump(res, open(os.path.join(W, "checks/out/j4b-r16-rawresult-keydiff.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
