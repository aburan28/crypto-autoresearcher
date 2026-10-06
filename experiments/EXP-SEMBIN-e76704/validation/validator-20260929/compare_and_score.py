import json, yaml
RUN="/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/runs/RUN-SEMBIN-79996f/"
res=json.load(open(RUN+"results.json")); mine=json.load(open("/tmp/claude-0/validator/rerun_fast.json"))
# 1. rerun vs results.json (ignore timing)
def strip(d): return {k:v for k,v in d.items() if k!="seconds"}
for k in ("T1_witness","T3_semaev_4_2","T4_null_4_2"):
    print(k, "rerun==results:", strip(mine["tests"][k])==strip(res["tests"][k]))
print("C1 rerun==results:", mine["controls"]["C1_kernel_regression"]==res["controls"]["C1_kernel_regression"])
print("C2 rerun==results:", mine["controls"]["C2_span_invariant"]==res["controls"]["C2_span_invariant"])
# 2. independent scoring against the SPEC text values (transcribed from specification.yaml preregistered_prediction.quantity)
SPEC={"T1_witness":{"D_ff_identity":2,"D_ff_M":3},
 "T2_semaev_6_3":{"group_order":9999360,"upward":1612800,"upward_zero_generator":0,"downward":0,"D_ff_identity":2,"D_ff_max":3},
 "T3_semaev_4_2":{"group_order":20160,"upward":0,"D_ff_identity":2,"D_ff_max":2},
 "T4_null_4_2":{"group_order":20160,"upward":5424,"D_ff_identity":2,"D_ff_max":3}}
man=json.load(open(RUN+"manifest.json"))
print("closed forms:", 31*30*28*24*16, 15*14*12*8)
allok=True
for k,p in SPEC.items():
    got=res["tests"][k]; checks={q:(got.get(q)==v) for q,v in p.items()}
    ok=all(checks.values()); allok&=ok
    pred_block={q:v for q,v in man["preregistered"][k].items() if q not in("cell","M")}
    print(k,"my_pass=",ok,"runner_pass=",res["verdict"][k]["pass_"],"runner_checks_equal=",res["verdict"][k]["checks"]==checks,"PRED==spec:",pred_block==p)
print("my all_predictions_confirmed:",allok,"runner:",res["all_predictions_confirmed"])
print("my controls_pass:", res["controls"]["C1_kernel_regression"]["all_match"] and res["controls"]["C2_span_invariant"], "runner:", res["controls_pass"])
# secondary unscored expected values
t1=res["tests"]["T1_witness"]
print("secondary T1:", t1["new_falls_identity"]==[0,1,15], t1["new_falls_M"]==[0,0,10], t1["degrees_identity"]==[2]*5, t1["degrees_M"]==[2,2,2,2,1])
print("secondary T3 downward 5376 (spec) vs runner:", res["tests"]["T3_semaev_4_2"]["downward"])
# manifest.yaml verdict transcription
my=yaml.safe_load(open(RUN+"manifest.yaml"))["run"]
print("manifest.yaml verdict:", my["result"]["verdict"], my["result"]["all_predictions_confirmed"], my["result"]["controls_pass"])
print("manifest.yaml src sha == manifest.json:", my["code"]["source_sha256"]==man["source_sha256"])
print("manifest.yaml preregistered == PRED:", my["inputs"]["preregistered"]==man["preregistered"])
