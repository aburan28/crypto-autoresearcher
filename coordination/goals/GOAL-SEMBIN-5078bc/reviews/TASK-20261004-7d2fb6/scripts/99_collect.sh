#!/bin/bash
# Copy the scratch result files into the write scope and write the instance manifest. Run last.
. $(dirname $0)/00_env.sh
D=$WS/outputs/scratch_results; mkdir -p $D
for f in w5_orig w5_mut w5_s32 w5_bigN w5_eq4 w5_eq4D7 xproc resume dose; do cp $SP/work/out/$f.jsonl $D/ 2>/dev/null; done
for f in w5_orig w5_mut w5_s32 w5_bigN w5_eq4 w5_eq4D7 xproc resume dose dose2; do cp $SP/work/out/$f.log $D/ 2>/dev/null; done
cp $SP/work/out/validate_ledger.txt $D/repo_validate_ledger_output.txt
cp $SP/m4ri_build_mine.log $D/m4ri_release-20240729_build_and_make_check_mine.log
mkdir -p $D/ref_stats; cp $SP/work/ref/*.stats $D/ref_stats/ 2>/dev/null
python3 - <<'PY'
import json, glob, os, hashlib
SP=os.environ["SP"]; out={}
for p in sorted(glob.glob(SP+"/work/inst/*.json")):
    if p.endswith(".lm_last"): continue
    d=json.load(open(p)); sysf=p[:-5]+".sys"
    out[d["name"]]={"N":d["N"],"n_equations":len(d["equations"]),"V_truth_table":d["V"],"max_degree":d["max_degree"],"system_sha256_boolsys_canonical":d["system_sha256"],"sys_file_sha256":hashlib.sha256(open(sysf,"rb").read()).hexdigest(),
                    "generator_args":{k:d[k] for k in ("n","m","t","k","draw")}}
json.dump(out, open(os.environ["WS"]+"/outputs/scratch_results/instances_manifest.json","w"), indent=1)
print(len(out),"instances in manifest")
PY
