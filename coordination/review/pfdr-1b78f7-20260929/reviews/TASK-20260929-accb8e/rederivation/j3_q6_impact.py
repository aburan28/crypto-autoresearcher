"""J3 Q6 impact: A1 SS cells recomputed with SS pairs at A_fix counted by the IC-5
definition (C(k',2) over formally distinct encodings, reconstructed from the retained
star rows; generic arms: nonformal = raw), wherever retention is complete for EVERY
census instance of the cell's four arms. Compared with A1 on the recorded
harvest-block field (the primary J3 computation). Labelled sensitivity; it replaces
no primary value."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j3_quantities as J
from common import OUT, MAIN_BITS, STRUCT, RAND, dump, rl


def main():
    p = os.path.join(OUT, "q6-blocks.json")
    rl.opened(p, "Q6 impact input: my own q6-blocks.json")
    blocks = json.load(open(p))
    rows = J.load_rows()
    idx = {}
    src = {}
    for lab in ["R10", "R11", "R12"]:
        for k, r in J.index(rows[lab]).items():
            idx[k] = r
            src[k] = lab
    idx16 = J.index(rows["R16"])
    for k in idx16:
        src[k] = "R16"

    def override(index, lab_of):
        """copy of the index with SS at_A_fix pairs replaced by the recount; returns
        (new index, set of keys whose block is incomplete or absent)."""
        new, incomplete = {}, set()
        for k, r in index.items():
            panel, m, b, j, arm, mode = k
            r2 = r
            if mode == "census" and r.get("status") == "completed_valid":
                bk = f"{lab_of(k)}|{b}|{j}|{m}|{arm}|{mode}|SS"
                v = blocks.get(bk)
                rec = r["harvest"]["SS"]["at_A_fix"]
                if r["harvest"]["SS"]["at_stop"]["rows_emitted"] == 0:
                    pass  # no SS rows at all: recount = 0 = recorded (checked below)
                elif v is None or not v["retention_complete"]:
                    incomplete.add(k)
                else:
                    r2 = json.loads(json.dumps(r))
                    r2["harvest"]["SS"]["at_A_fix"]["pairs_nonformal"] = v["ss_pairs_raw_at_A_fix_recomputed"]
                    r2["harvest"]["SS"]["at_A_fix"]["pairs_raw"] = v["ss_pairs_raw_at_A_fix_recomputed"]
            new[k] = r2
        return new, incomplete

    idx_o, inc = override(idx, lambda k: src[k])
    out = {"main": [], "stage_r": []}
    exc_rec, exc_new = [], []
    for m in [3, 4, 5]:
        for b in MAIN_BITS:
            for A in STRUCT:
                keys = [("main", m, b, j, a, "census") for j in range(5) for a in [A] + RAND[A]]
                c0 = J.a1_cell(idx, "main", m, b, range(5), A, RAND[A], "SS")
                if any(k in inc for k in keys):
                    out["main"].append({"arm": A, "m": m, "bits": b, "recomputable": False,
                                        "z_recorded": c0["z"], "resolved": c0["resolved"]})
                    if c0["resolved"] and c0["z"] is not None and abs(c0["z"]) > 3:
                        exc_rec.append([A, m, b])
                    continue
                c1 = J.a1_cell(idx_o, "main", m, b, range(5), A, RAND[A], "SS")
                out["main"].append({"arm": A, "m": m, "bits": b, "recomputable": True,
                                    "z_recorded": c0["z"], "z_recount": c1["z"], "kappa_recorded": c0["kappa"],
                                    "kappa_recount": c1["kappa"], "C_A": [c0["C_A"], c1["C_A"]],
                                    "C_R": [c0["C_R"], c1["C_R"]], "resolved": [c0["resolved"], c1["resolved"]]})
                if c0["resolved"] and c0["z"] is not None and abs(c0["z"]) > 3:
                    exc_rec.append([A, m, b])
                if c1["resolved"] and c1["z"] is not None and abs(c1["z"]) > 3:
                    exc_new.append([A, m, b])
    idx16_o, inc16 = override(idx16, lambda k: "R16")
    for (A, m, b) in [("small_x", 4, 20), ("dickson", 4, 26)]:
        keys = [("main", m, b, j, a, "census") for j in range(5, 10) for a in [A] + RAND[A]]
        c0 = J.a1_cell(idx16, "main", m, b, range(5, 10), A, RAND[A], "SS")
        if any(k in inc16 for k in keys):
            out["stage_r"].append({"arm": A, "m": m, "bits": b, "recomputable": False, "z_recorded": c0["z"]})
            continue
        c1 = J.a1_cell(idx16_o, "main", m, b, range(5, 10), A, RAND[A], "SS")
        out["stage_r"].append({"arm": A, "m": m, "bits": b, "recomputable": True, "z_recorded": c0["z"],
                               "z_recount": c1["z"], "C_A": [c0["C_A"], c1["C_A"]], "C_R": [c0["C_R"], c1["C_R"]]})
    out["SS_excursions_recorded_fields"] = exc_rec
    out["SS_excursions_recount_where_recomputable"] = exc_new
    out["cells_not_recomputable"] = sum(1 for x in out["main"] if not x["recomputable"])
    out["cells_recomputable"] = sum(1 for x in out["main"] if x["recomputable"])
    dump("q6-impact.json", out)
    for x in out["main"]:
        if x["recomputable"] and x["z_recorded"] is not None and x["z_recount"] is not None and abs(x["z_recorded"] - x["z_recount"]) > 0.25:
            print("moved:", x)
    print("stage_r", out["stage_r"])
    print("exc recorded", exc_rec, "exc recount", exc_new, "recomputable", out["cells_recomputable"], "not", out["cells_not_recomputable"])


if __name__ == "__main__":
    main()
