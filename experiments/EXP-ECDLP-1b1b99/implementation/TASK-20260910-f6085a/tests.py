"""Deterministic artificial controls for the pure CM cost component.

No curves, maps, certificates, runner, lock, nonce, or scientific measurement
is constructed here.  The named controls are frozen in coverage.json.
"""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from costs import CostError, allocate_equal, actual_campaign_accounting, canonical_json, canonical_targets, strict_json_loads, validate_allocation_edges, validate_raw_rows
from reducers import ReductionError, hard_validity, q_star, reduce_primary, select_baselines

def leaf(name: str, **more):
    row = {"record_type":"raw_cost","raw_cost_row_id":name,"physical_event_id":"ev-"+name,"event_ordinal":0,"component":"scalar_multiplication","phase":"evaluation","status":"complete","CPU_nanoseconds":17,"CPU_unavailable_reason":None,"wall_nanoseconds":19,"wall_unavailable_reason":None,"process_group_peak_RSS_bytes":31,"RSS_unavailable_reason":None,"operation_counts":None,"operation_counts_unavailable_reason":"uninstrumented_backend","capture_interval":{"stream_id":name,"process_group_id":1,"cpu_started_ns":0,"cpu_finished_ns":17,"wall_started_ns":0,"wall_finished_ns":19,"reason":None},"charge_kind":"exclusive_leaf","source_leaf_ids":[],"scope":"block_repetition","fixture":"I0F0","endpoint":"K0","coordinate":1,"plane":"main","seed":606103,"q":4096,"arm":2,"block":0,"repetition":1}
    row.update(more); return row
def blocks(fixed: int, cpu: int): return [{"block":b,"CPU_nanoseconds":cpu,"repetitions":1,"status":"complete"} for b in range(7)]
def control(name, body):
    try: body(); return {"id":name,"outcome":"pass"}
    except Exception as exc: return {"id":name,"outcome":"fail","error":repr(exc)}
def must_fail(body):
    try: body()
    except (CostError, ReductionError): return
    raise AssertionError("known-invalid input was admitted")
def require(value):
    if not value: raise AssertionError("required predicate was false")
def selection_rows():
    rows=[]
    for i in range(3):
      for coordinate in (1,2,3):
       for arm in range(2,8):
        for endpoint in range(8):
         for block in range(7): rows.append({"interval":f"I{i}","coordinate":coordinate,"candidate_arm":arm,"endpoint":f"E{endpoint}","block":block,"CPU_nanoseconds":10+arm,"repetitions":1,"setup_CPU_nanoseconds":1 if block==0 else 0})
    return rows
def panel(ratio_cpu=12):
    cells={}
    for fixture in ("I0F0","I0F1","I1F0","I1F1","I2F0","I2F1"):
      for cls in ("C0","C1"):
       for coordinate in (1,2,3): cells[(fixture,cls,coordinate)]={"scalar":[{"fixed_CPU_nanoseconds":0,"blocks":blocks(0,ratio_cpu)} for _ in range(2)],"transport":[{"fixed_CPU_nanoseconds":0,"blocks":blocks(0,10)} for _ in range(2)]}
    return cells
def run():
    controls=[]
    controls.append(control("CMC-001-strict-json-duplicate", lambda: must_fail(lambda: strict_json_loads('{"x":1,"x":2}'))))
    controls.append(control("CMC-002-strict-json-float", lambda: must_fail(lambda: strict_json_loads('{"x":1.0}'))))
    controls.append(control("CMC-003-canonical-float", lambda: must_fail(lambda: canonical_json({"x":1.0}))))
    controls.append(control("CMC-004-valid-leaf", lambda: validate_raw_rows([leaf("a")])) )
    controls.append(control("CMC-005-duplicate-event", lambda: must_fail(lambda: validate_raw_rows([leaf("a"),leaf("b",physical_event_id="ev-a")]))))
    controls.append(control("CMC-006-integral-bool-axis", lambda: must_fail(lambda: validate_raw_rows([leaf("a", coordinate=True)]))))
    controls.append(control("CMC-007-noncanonical-plane", lambda: must_fail(lambda: validate_raw_rows([leaf("a", plane="MAIN")]))) )
    controls.append(control("CMC-008-unavailable-pair", lambda: must_fail(lambda: validate_raw_rows([leaf("a", CPU_nanoseconds=None, CPU_unavailable_reason=None)]))))
    controls.append(control("CMC-009-derived-rollup", lambda: validate_raw_rows([leaf("a"),leaf("roll",event_ordinal=1,charge_kind="derived_rollup",source_leaf_ids=["a"],CPU_nanoseconds=None,CPU_unavailable_reason="derived_rollup",wall_nanoseconds=None,wall_unavailable_reason="derived_rollup",process_group_peak_RSS_bytes=None,RSS_unavailable_reason="derived_rollup",capture_interval={"stream_id":"roll","process_group_id":1,"cpu_started_ns":None,"cpu_finished_ns":None,"wall_started_ns":None,"wall_finished_ns":None,"reason":"derived_rollup"})])))
    controls.append(control("CMC-010-prefix-class-shape", lambda: canonical_targets({f:("K0","K1","K2","K3") for f in ("I0F0","I0F1","I1F0","I1F1","I2F0","I2F1")},{f:("K0","K1","K2","K3") for f in ("I0F0","I0F1","I1F0","I1F1","I2F0","I2F1")})))
    def split():
      r=leaf("a",CPU_nanoseconds=17,wall_nanoseconds=19); es=allocate_equal(r,strategy_view="scalar",scenario={"kind":"cold","q":1,"seed":606101},targets=[{"kind":"endpoint_coordinate","fixture":"I0F0","endpoint":"K0","coordinate":1},{"kind":"endpoint_coordinate","fixture":"I0F0","endpoint":"K1","coordinate":1}],reason_code="shared_setup"); validate_allocation_edges([r],es); assert [e["allocated_CPU_nanoseconds"] for e in es]==[9,8]
    controls.append(control("CMC-011-integer-remainder",split))
    controls.append(control("CMC-012-bad-edge-sum",lambda: must_fail(lambda: validate_allocation_edges([leaf("a")],[]))))
    controls.append(control("CMC-013-actual-once",lambda: (lambda x: (assert_actual(x)))(actual_campaign_accounting([leaf("a")]))))
    controls.append(control("CMC-014-selection-9x6x8x7",lambda: select_baselines(selection_rows())))
    controls.append(control("CMC-015-selection-missing",lambda: must_fail(lambda: select_baselines(selection_rows()[:-1]))))
    controls.append(control("CMC-016-selection-tie-low-arm",lambda: assert_selection_tie()))
    controls.append(control("CMC-017-288-cell-alternatives",lambda: require(len(panel())*8==288)))
    controls.append(control("CMC-018-36-governing-cells",lambda: require(len(panel())==36)))
    controls.append(control("CMC-019-positive-full-loo",lambda: require(reduce_primary(panel())["classification"]=="success_stable")))
    controls.append(control("CMC-020-negative-full-loo",lambda: require(reduce_primary(panel(10))["classification"]=="negative_stable")))
    controls.append(control("CMC-021-mixed-inconclusive",lambda: require(reduce_primary(panel(11))["classification"]=="statistically_inconclusive")))
    bad=panel(); bad[("I0F0","C0",1)]["scalar"][0]["blocks"][0]["below_resolution"]=True
    controls.append(control("CMC-022-below-resolution-unresolved",lambda: require(reduce_primary(bad)["state"]=="unresolved")))
    controls.append(control("CMC-023-qstar-first-crossing",lambda: require(q_star({1:{"numerator":1,"denominator":2},16:{"numerator":1,"denominator":1},256:{"numerator":2,"denominator":1},4096:{"numerator":2,"denominator":1}})==16)))
    controls.append(control("CMC-024-qstar-equality-boundary",lambda: require(q_star({1:{"numerator":1,"denominator":1},16:{"numerator":2,"denominator":1},256:{"numerator":2,"denominator":1},4096:{"numerator":2,"denominator":1}})==1)))
    controls.append(control("CMC-025-hard-validity-empty",lambda: require(hard_validity({}) is False)))
    controls.append(control("CMC-026-hard-validity-explicit-false",lambda: require(hard_validity({"authorization_and_nonce_valid":False}) is False)))
    if any(item["outcome"] != "pass" for item in controls): raise AssertionError(json.dumps(controls,indent=2))
    return controls
def assert_actual(value): assert value["status"]=="valid" and value["CPU_nanoseconds"]==17 and value["peak_RSS_bytes"]==31
def assert_selection_tie():
    rows=selection_rows()
    for r in rows: r["CPU_nanoseconds"]=10
    assert all(a==2 for a in select_baselines(rows).values())
if __name__ == "__main__": print(json.dumps({"controls":run()},sort_keys=True))
