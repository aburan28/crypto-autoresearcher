#!/bin/bash
# B6.1/B6.2/B6.3 from GitHub metadata: for each archived run, head_sha + start time; protocol.json at head_sha
# (sha256 vs main); every run of the same workflow file (forking paths / unarchived runs).
OUT=$1
declare -A WF=( [39305259093]=n83-closure.yml [39335956567]=n83-closure-indexlift.yml [39359922687]=n83-closure-indexlift-rep.yml [39383739494]=n83-indexbuild.yml [39464544962]=n83-indexbuild2.yml [39527997793]=n83-rankfinder.yml [39527549698]=n83-onlineframe2.yml [39303742695]=n83-onlineframe.yml [39007026856]=n83-replay.yml )
declare -A EX=( [39305259093]=koblitz-n83-closure-20261019 [39335956567]=koblitz-n83-closure-indexlift-20261019 [39359922687]=koblitz-n83-closure-indexlift-rep-20261020 [39383739494]=koblitz-n83-indexbuild-20261020 [39464544962]=koblitz-n83-indexbuild2-20261020 [39527997793]=koblitz-n83-rankfinder-20261021 [39527549698]=koblitz-n83-onlineframe2-20261021 [39303742695]=koblitz-n83-onlineframe-20261019 [39007026856]=koblitz-n83-replay-20261017 )
for run in "${!WF[@]}"; do
  meta=$(timeout 60 gh api repos/aburan28/cryptanalysis/actions/runs/$run --jq '[.head_sha,.head_branch,.run_started_at,.conclusion]|@tsv')
  sha=$(echo "$meta" | cut -f1)
  e=${EX[$run]}
  pfile=protocol.json; [ "$run" = 39007026856 ] && pfile=PROTOCOL.md
  at_head=$(timeout 60 gh api -H "Accept: application/vnd.github.raw" "repos/aburan28/cryptanalysis/contents/experiments/$e/$pfile?ref=$sha" 2>/dev/null | sha256sum | cut -c1-16)
  on_main=$(cd /home/user/aburan28/cryptanalysis && git -c gc.auto=0 show HEAD:experiments/$e/$pfile | sha256sum | cut -c1-16)
  pcommits=$(timeout 60 gh api "repos/aburan28/cryptanalysis/commits?sha=$sha&path=experiments/$e/$pfile&per_page=20" --jq '[.[]|(.sha[0:9]+"@"+.commit.committer.date)]|join(",")')
  runs=$(timeout 60 gh api "repos/aburan28/cryptanalysis/actions/workflows/${WF[$run]}/runs?per_page=50" --jq '[.workflow_runs[]|("\(.id):\(.conclusion):\(.head_sha[0:9]):\(.run_started_at)")]|join(" ")')
  echo -e "run=$run exp=$e\n  meta=$meta\n  protocol_at_head=$at_head protocol_on_main=$on_main\n  protocol_commits_on_branch=$pcommits\n  workflow_runs=$runs" 
done > $OUT
