# Verbatim copy (written after the run) of the read-only inline command that produced
# scratch/c7_corrected.json; run as:  cd scratch && python3 -B - < this-code > c7_corrected.json
# Read-only re-evaluation of small_checks C7 (its cofactor predicate treated a certified integer cofactor as missing).
import json, yaml, os
PRIMARY = ["order_certificate","cofactor","embedding_degree","cm_discriminant_bits","twist_order_factorization","twist_security_bits","rigidity_reproduced","figure_provenance_table"]
out = {"note": "Corrected evaluation of the frozen success criterion on each proves-too-much output. cofactor counts as present if it is an integer (derived from a certified order) or if the order_certificate not_verifiable reason covers it.", "objects": {}}
for obj in ["objA_supersingular","objB_subfield","objC_tampered_selfreports","objD_mas_shifted_rigidity","objD_gf_shifted_rigidity"]:
    r = json.load(open(f"objects/{obj}/out/raw-result.json")); m = r["metrics"]; nv = r["not_verifiable"]
    tab = yaml.safe_load(open(f"objects/{obj}/out/audit-table.yaml"))["audit_table"]
    ids = [f["id"] for f in yaml.safe_load(open(f"objects/{obj}/out/figure-provenance.yaml"))["figure_provenance"]["figures"]]
    per = {}
    for k in PRIMARY:
        v = m.get(k)
        if k == "cofactor":
            ok = isinstance(v, int) or ("order_certificate" in nv)
            how = "certified integer" if isinstance(v, int) else ("covered only by the order_certificate not_verifiable reason" if ok else "missing")
        elif k == "figure_provenance_table":
            ok = v == "present"; how = v
        else:
            ok = (isinstance(v, str) and v.startswith("certificate")) or (v in ("not_verifiable", "bound") and any(k.split("_")[0] in kk for kk in nv))
            how = v if isinstance(v, str) else str(v)
        per[k] = {"value": how, "ok": ok}
    control = [x["result"] for x in tab["rows"] if x["criterion"] == "scurve_control_certificate_match"][0]
    tags = ("field_security_142" in ids) and ("twist_security_101_93" in ids or tab["curve_id"] == "EcGFp5")
    out["objects"][obj] = {"per_metric": per, "control_row": control, "required_tags_present": tags,
                           "success_criterion_met": all(x["ok"] for x in per.values()) and control.startswith("PASS") and tags,
                           "met_only_via_order_reason_for_cofactor": per["cofactor"]["value"].startswith("covered")}
print(json.dumps(out, indent=2))
