#!/bin/sh
# Frozen native trial commands plus metadata/receipt orchestration only.
set -u
# Wait for the already published goal claim before any scientific command.
launch_wait=0
while [ ! -f /private/tmp/isou-compact-m8191-145d29/launch-authorized.flag ] && [ "$launch_wait" -lt 900 ]; do sleep 1; launch_wait=$((launch_wait+1)); done
if [ ! -f /private/tmp/isou-compact-m8191-145d29/launch-authorized.flag ]; then echo 'Scientific launch not authorized; no native trial started.'; exit 75; fi
cd /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015 || exit 70
execution='coordination/goals/GOAL-ISOU-f30a07/batches/BATCH-9924e2/final-e82/execution/TASK-20261016-145d29'
adapter='coordination/goals/GOAL-ISOU-f30a07/batches/BATCH-9924e2/final-e82/native-command.sh'
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$execution/started-utc.txt"
prepare_metadata() {
  python3 - "$1" "$2" <<'PYMETA'
import datetime,json,subprocess,sys
from pathlib import Path
run=Path(sys.argv[1]);mode=sys.argv[2]
assert not run.exists(), 'fresh run required'
run.mkdir(parents=True)
def read(argv): return subprocess.check_output(argv,text=True).strip()
argv=['/bin/sh','coordination/goals/GOAL-ISOU-f30a07/batches/BATCH-9924e2/final-e82/native-command.sh',mode,str(run)]
env={'schema':'isogeny-native-execution-environment/v1','collected_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':{'cpu_model':read(['/usr/sbin/sysctl','-n','machdep.cpu.brand_string']),'memory_bytes':int(read(['/usr/sbin/sysctl','-n','hw.memsize'])),'logical_cpus':int(read(['/usr/sbin/sysctl','-n','hw.logicalcpu'])),'kernel_arch':read(['/usr/bin/uname','-sm']),'macos_version':read(['/usr/bin/sw_vers','-productVersion']),'load_average':read(['/usr/sbin/sysctl','-n','vm.loadavg']),'shared_host':True},'source_repository':'aburan28/crypto','source_commit':'e82d80feaf82d3730576ccd9137911b336f9dab8','source_dirty':False,'binary_sha256':'b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b','harness_commit':read(['git','rev-parse','HEAD']),'harness_branch':read(['git','branch','--show-current']),'argv':argv,'goal':'GOAL-ISOU-f30a07','task':'TASK-20261016-145d29','approval':'DEC-20261016-34a9e9','execution':'direct native executable via frozen thin shell receipt adapter; Python used only for metadata','selected_continuation_queue':'coordination/goals/GOAL-ISOU-f30a07/batches/BATCH-9924e2/final-e82-report-completion/dispatch_queue.json','selected_continuation_queue_sha256':'dcb5374e6dcaef2809e7f50f722073364ca8224517991a8087cde5cb2f427328','original_trial_plan_sha256':'76e6cedc60c78b9d4553058934d0aed06270c3958a5ff98b04a233f70ffabc98','actual_served_model':None,'actual_served_effort':None}
with (run/'environment.json').open('x') as f:f.write(json.dumps(env,indent=2)+'\n')
with (run/'command.txt').open('x') as f:f.write(' '.join(argv)+'\n')
PYMETA
}
construct='/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-feb102/runs/RUN-ISOU-bdbf5d'
verify='/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-feb102/runs/RUN-ISOU-2b2372'
if ! prepare_metadata "$construct" construct; then
  printf '%s\n' 'Constructor metadata setup failed before native invocation; preserve files and inspect. No retry.' > "$execution/setup-failure.txt"
  exit 74
fi
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$execution/construct-started-utc.txt"
/bin/sh "$adapter" construct "$construct" > "$construct/stdout.log" 2> "$construct/stderr.log"
construct_adapter_exit=$?
printf '%s\n' "$construct_adapter_exit" > "$execution/construct-adapter.exit-code.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$execution/construct-ended-utc.txt"
if ! prepare_metadata "$verify" verify; then
  printf '%s\n' 'Verification metadata setup failed before adapter invocation; preserve files and inspect. No retry.' > "$execution/verify-setup-failure.txt"
  exit 74
fi
# This is the adapter invocation time. Its frozen conditional gate records
# NOT_STARTED if construction or the sealed certificate is unsuitable.
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$execution/verify-adapter-invoked-utc.txt"
/bin/sh "$adapter" verify "$verify" > "$verify/stdout.log" 2> "$verify/stderr.log"
verify_adapter_exit=$?
printf '%s\n' "$verify_adapter_exit" > "$execution/verify-adapter.exit-code.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$execution/verify-adapter-ended-utc.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$execution/ended-utc.txt"
printf '%s\n' 'Both frozen adapters are terminal; actual native results remain authoritative.'
n=0
while [ ! -f /private/tmp/isou-compact-m8191-145d29/postprocessing.done ] && [ "$n" -lt 360 ]; do
  sleep 20
  n=$((n+1))
done
if [ ! -f /private/tmp/isou-compact-m8191-145d29/postprocessing.done ]; then
  printf '%s\n' 'Postprocessing was not acknowledged within two hours; preserve terminal receipts.'
  exit 124
fi
/Users/adamburan/.local/bin/conductor task release T-3252
