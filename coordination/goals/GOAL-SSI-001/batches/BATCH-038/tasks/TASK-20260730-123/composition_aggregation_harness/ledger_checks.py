from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
try:
    import yaml
except ImportError:
    yaml = None

EXPECTED_COUNTS = {'total_items': 39, 'composition_law_surface_family': 6, 'peak_aggregation_feed_family': 5, 'global_bound_input_feed_family': 5, 'charge_metering_feed_family': 4, 'composition_field_placeholder_family': 5, 'lineage_cross_link_family': 14, 'wired_symbolic': 25, 'checklist_only': 1, 'not_instantiated': 9, 'not_supported': 4, 'deferred': 0}

ALLOWED_STATUS = frozenset(["wired_symbolic","checklist_only","not_instantiated","not_supported","deferred"])
ALLOWED_FAMILIES = frozenset([
  "composition_law_surface","peak_aggregation_feed","global_bound_input_feed",
  "charge_metering_feed","composition_field_placeholder","lineage_cross_link",
])

def task_dir() -> Path:
    return Path(__file__).resolve().parents[1]

def load_yaml(name: str) -> Dict[str, Any]:
    data = yaml.safe_load((task_dir()/name).read_text())
    if not isinstance(data, dict):
        raise ValueError(name)
    return data

def check_obligation_ledger() -> Dict[str, Any]:
    root = load_yaml("composition_aggregation_schema_ledger.yaml")["composition_aggregation_schema_ledger"]
    items = root["items"]
    fam = {f:0 for f in ALLOWED_FAMILIES}
    st = {s:0 for s in ALLOWED_STATUS}
    for it in items:
        fam[it["family"]] = fam.get(it["family"],0)+1
        st[it["status"]] = st.get(it["status"],0)+1
    summary = root["summary"]
    edge_ok = (
        len(items)==EXPECTED_COUNTS["total_items"]
        and fam["composition_law_surface"]==EXPECTED_COUNTS["composition_law_surface_family"]
        and fam["peak_aggregation_feed"]==EXPECTED_COUNTS["peak_aggregation_feed_family"]
        and fam["global_bound_input_feed"]==EXPECTED_COUNTS["global_bound_input_feed_family"]
        and fam["charge_metering_feed"]==EXPECTED_COUNTS["charge_metering_feed_family"]
        and fam["composition_field_placeholder"]==EXPECTED_COUNTS["composition_field_placeholder_family"]
        and fam["lineage_cross_link"]==EXPECTED_COUNTS["lineage_cross_link_family"]
        and st["wired_symbolic"]==EXPECTED_COUNTS["wired_symbolic"]
        and st["checklist_only"]==EXPECTED_COUNTS["checklist_only"]
        and st["not_instantiated"]==EXPECTED_COUNTS["not_instantiated"]
        and st["not_supported"]==EXPECTED_COUNTS["not_supported"]
    )
    package_ok = (
        summary.get("ledger_status")=="composition_aggregation_schema_partial"
        and summary.get("control_result")=="FAIL"
        and summary.get("query_memory_cleared") is False
        and summary.get("composition_operator_invented") is False
        and summary.get("aggregation_factor_invented") is False
        and summary.get("tau_invented") is False
    )
    return {"edge_counts_ok": edge_ok, "package_ok": package_ok, "item_count": len(items),
            "family_counts": fam, "status_counts": st, "ledger_status": summary.get("ledger_status"),
            "control_result": summary.get("control_result"), "query_memory_cleared": summary.get("query_memory_cleared")}

def check_memory_map_status() -> Dict[str, Any]:
    qm = load_yaml("memory_map_status.yaml")["memory_map_status"]["qm_memory_map"]
    passed = (qm.get("prior_status")=="global_memory_bound_schema_partial"
              and qm.get("status_after_batch")=="composition_aggregation_schema_partial"
              and qm.get("clearance") is False and qm.get("query_memory_cleared") is False)
    return {"passed": passed, "prior_status": qm.get("prior_status"), "status_after_batch": qm.get("status_after_batch"),
            "clearance": qm.get("clearance"), "query_memory_cleared": qm.get("query_memory_cleared")}

def check_classification() -> Dict[str, Any]:
    data = load_yaml("classification.yaml")["classification"]
    passed = (data.get("disposition")=="FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
              and data.get("control_result")=="FAIL" and data.get("non_extrapolation") is True)
    return {"passed": passed, "disposition": data.get("disposition")}

def check_mutation_status() -> Dict[str, Any]:
    data = load_yaml("mutation_status.yaml")["mutation_status"]
    passed = (data["QM_MEMORY_MAP"]["status_after_batch"]=="composition_aggregation_schema_partial"
              and data["QM_STOPPING"]["control_result"]=="FAIL"
              and data["QUERY_MEMORY"]["cleared"] is False)
    return {"passed": passed}

def check_no_invented_numerics() -> Dict[str, Any]:
    hits=[]
    for name in ("composition_aggregation_schema_ledger.yaml","memory_map_status.yaml","mutation_status.yaml","classification.yaml"):
        data=load_yaml(name)
        def visit(obj, path="$"):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    p=f"{path}.{k}"
                    if k in ("composition_operator","aggregation_factor") and v not in (None,"not_instantiated","unresolved","not_supported","null"):
                        if not isinstance(v,(dict,list)):
                            hits.append({"path":p,"key":k,"value":v,"file":name})
                    if k in ("query_memory_cleared","composition_operator_invented","aggregation_factor_invented","tau_invented","clearance","pin_complete") and v is True:
                        hits.append({"path":p,"key":k,"value":v,"file":name,"reason":"forbidden_true"})
                    visit(v,p)
            elif isinstance(obj,list):
                for i,v in enumerate(obj):
                    visit(v,f"{path}[{i}]")
        visit(data)
    return {"hits":hits,"passed":len(hits)==0}
