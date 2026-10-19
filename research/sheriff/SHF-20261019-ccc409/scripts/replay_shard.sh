#!/bin/bash
# usage: replay_shard.sh N   (N = shard index). Sparse scratch worktree, replays shards/replayN.txt, writes shards/replay_outN.jsonl
set -u
N=$1
REPO=/home/user/crypto-autoresearcher
CASE=$REPO/research/sheriff/SHF-20261019-ccc409
WT=/tmp/claude-0/-home-user-crypto-autoresearcher/1a2f68ea-e21c-5336-90b8-76c46a47774f/scratchpad/wt$N
cd $REPO
DIRS=$(python3 -I - <<PY
import json
ids=set(open("$CASE/shards/replay$N.txt").read().split())
d=set()
for l in open("$CASE/shards/all.jsonl"):
    r=json.loads(l)
    if r["evidence_id"] in ids and r.get("replay_command_file"):
        p=r["replay_command_file"].split("/"); d.add("/".join(p[:2]))
print(" ".join(sorted(d)))
PY
)
git worktree add -q --no-checkout --detach $WT 7dbe0298d5
cd $WT && git sparse-checkout set --cone tools src harness scripts schemas config tests $DIRS && git checkout -q 7dbe0298d5
echo "worktree ready: $(du -sh $WT | cut -f1), $(git -C $WT ls-files -t | grep -vc "^S") files checked out"
cd $REPO
python3 -I $CASE/scripts/replay.py run $WT $(cat $CASE/shards/replay$N.txt) > $CASE/shards/replay_out$N.jsonl
echo "done $(wc -l < $CASE/shards/replay_out$N.jsonl) rows"
git worktree remove --force $WT
