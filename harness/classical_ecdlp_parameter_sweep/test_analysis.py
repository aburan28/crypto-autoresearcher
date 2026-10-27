"""Synthetic disjoint-cost, shared-reference and incomplete-panel checks."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


a=load("_sweep_analysis_tested","analysis.py")
e=load("_sweep_export_tested","export.py")


def native_rows(cell="cell",fixture="fixture",rep=0,arm="harvest",target_cost=1):
    def row(kind,**fields):
        return {"schema":a.NATIVE_SCHEMA,"scope":a.NATIVE_SCOPE,"row_kind":kind,
                "cell_id":cell,"fixture":fixture,"replicate":rep,"arm":arm,**fields}
    def counters(group):
        return {"group_additions":group,"scalar_multiplications":900,"field_multiplications":7000}
    rows=[row("fixture_validation",counters=counters(100),target_count=64),
          row("setup",counters=counters(10)),
          row("lookup",counters=counters(1000000),auxiliary_work={"hash_calls":2**63+17})]
    rows += [row("target",target_id="q"+str(i),target_ordinal=i,status="solved",verified_scalar=i,
                 counters=counters(target_cost)) for i in range(64)]
    return rows


def child_panel(variant,arm,fixture,rep):
    cell=fixture+"-"+str(rep)+"--"+variant
    cost=1 if arm=="harvest" else 2
    rows=native_rows(cell,fixture,rep,arm,cost)
    panel=a.summarize_stream(rows,["q"+str(i) for i in range(64)],(cell,fixture,rep,arm))
    return {"arm_id":variant+"."+arm,"variant":variant,"arm":arm,"fixture_id":fixture,"replicate":rep,
            "cell_id":cell,"status":"completed","attempts":1,"analysis":panel,"findings":[],"verification_passed":True,
            "raw":None,"execution":"cells/"+cell+"/"+arm+"/execution.json"}


def complete_children():
    return [child_panel(variant,arm,fixture,rep)
            for fixture in ("f0","f1") for rep in (0,1)
            for variant,arm in [(v,x) for v in a.VARIANTS for x in a.BL_ARMS]+[("shared","rho_reference")]]


class CostAndCoverageTests(unittest.TestCase):
    def test_only_disjoint_counted_phases_no_scalar_or_event_double_charge(self):
        rows=native_rows();panel=a.summarize_stream(rows,["q"+str(i) for i in range(64)],("cell","fixture",0,"harvest"))
        self.assertEqual(panel["prefixes"]["64"]["full_native_counters"]["group_additions"],174)
        self.assertEqual(panel["prefixes"]["64"]["solver_api_counters"]["group_additions"],74)
        self.assertEqual(panel["prefixes"]["1"]["full_native_counters"]["group_additions"],111)
        self.assertEqual(panel["prefixes"]["64"]["full_native_counters"]["scalar_multiplications"],66*900)

    def test_counter_sequences_keep_large_integer_exact_not_float_weight(self):
        values=a.native_counter_sequences(native_rows())
        self.assertEqual(json.loads(values["native.lookup.auxiliary_work.hash_calls"]),[2**63+17])
        self.assertEqual(json.loads(values["native.target.counters.group_additions"]),[1]*64)

    def test_shared_rho_observed_once_and_same_curve_bootstrap(self):
        children=complete_children();result=a.summarize(children,"a"*64,"b"*64,repetitions=40,expected_curves=2)
        self.assertEqual(len(children),164)
        self.assertEqual(result["shared_rho_observation_rows"],4)
        self.assertEqual(result["aa_mismatches"],[])
        primary=next(x for x in result["comparisons"] if x["variant"]==a.VARIANTS[0]
                     and x["baseline"].endswith(".static_small") and x["metric"]=="full_native_group_additions_m64")
        self.assertAlmostEqual(primary["gmean_ratio"],174/238)
        self.assertEqual(primary["pointwise_cluster_bootstrap_ci95"],[primary["gmean_ratio"],primary["gmean_ratio"]])
        with self.assertRaisesRegex(ValueError,"duplicate observed"):
            a.summarize(children+[children[-1]],"a"*64,"b"*64,repetitions=2,expected_curves=2)
        children[-1]["attempts"]=0
        partial=a.summarize(children,"a"*64,"b"*64,repetitions=2,expected_curves=2)
        self.assertEqual(partial["shared_rho_planned_slots"],4)
        self.assertEqual(partial["shared_rho_observation_rows"],3)
        self.assertEqual(partial["shared_rho_unattempted_slots"],1)
        self.assertTrue(all("undefined_reason" in x for x in partial["comparisons"] if x["baseline"]=="shared.rho_reference"))

    def test_missing_or_censored_target_never_creates_success_only_ratio(self):
        children=complete_children();candidate=next(x for x in children if x["arm_id"]==a.VARIANTS[0]+".harvest")
        rows=native_rows(candidate["cell_id"],candidate["fixture_id"],candidate["replicate"],"harvest")[:-1]
        candidate["analysis"]=a.summarize_stream(rows,["q"+str(i) for i in range(64)],
            (candidate["cell_id"],candidate["fixture_id"],candidate["replicate"],"harvest"))
        self.assertFalse(candidate["analysis"]["output_complete"])
        self.assertEqual(candidate["analysis"]["observed_full_native_counters"]["group_additions"],173)
        result=a.summarize(children,"a"*64,"b"*64,repetitions=4,expected_curves=2)
        affected=[x for x in result["comparisons"] if x["variant"]==a.VARIANTS[0]]
        self.assertTrue(all("gmean_ratio" not in x and "undefined_reason" in x for x in affected))
        candidate["analysis"]=copy.deepcopy(children[1]["analysis"])
        candidate["analysis"]["all_targets_solved"]=False
        result=a.summarize(children,"a"*64,"b"*64,repetitions=4,expected_curves=2)
        self.assertTrue(all("gmean_ratio" not in x for x in result["comparisons"] if x["variant"]==a.VARIANTS[0]))

    def test_duplicate_counted_phase_refuses_and_noninteger_counters_refuse(self):
        rows=native_rows();ids=["q"+str(i) for i in range(64)]
        with self.assertRaisesRegex(ValueError,"duplicate counted"):
            a.summarize_stream(rows+[rows[0]],ids,("cell","fixture",0,"harvest"))
        rows[0]["counters"]["group_additions"]=1.5
        with self.assertRaisesRegex(ValueError,"exact integers"):
            a.summarize_stream(rows,ids,("cell","fixture",0,"harvest"))

    def test_export_has_41_distinct_arms_shared_rho_once_rusage_once(self):
        children=complete_children();provider={"app_id":"ap-SYNTHETIC","sandbox_id":"sb-SYNTHETIC","image_id":"im-SYNTHETIC"}
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);files={}
            for child in children:
                path=root/child["execution"];path.parent.mkdir(parents=True);path.write_text("{}")
                files[child["execution"]]={"path":child["execution"],"sha256":a.sha(path),"bytes":2}
                child["metadata"]={"status":"completed","exitcode":0,"provider_identity":provider,"solver_seed":123,
                                   "rusage":{"user_seconds":.25,"system_seconds":.125,"maxrss_bytes":12345},
                                   "clock":{"wall_seconds":1,"wall_valid":False},"host_before":{},"resumed":False}
            rows,unattempted,unresolved=e.execution_rows(children,root,files,provider,root)
            self.assertEqual(len(rows),164);self.assertEqual(len({r["arm"] for r in rows}),41)
            self.assertEqual(sum(r["arm"]=="shared.rho_reference" for r in rows),4)
            self.assertEqual(sum(r["measurements"]["cpu_user_seconds"] for r in rows),164*.25)
            self.assertEqual(unattempted,[]);self.assertEqual(unresolved,[])
            self.assertTrue(all(r["measurements"]["wall_valid"] is False for r in rows))
            # A declared slot is not a completed process merely to satisfy the
            # export schema: known zero and unresolved attempts remain separate.
            children[0]["attempts"]=0;children[1]["attempts"]=None
            rows,unattempted,unresolved=e.execution_rows(children,root,files,provider,root)
            self.assertEqual(len(rows),162);self.assertEqual(len(unattempted),1);self.assertEqual(len(unresolved),1)
            self.assertEqual(unattempted[0]["attempts"],0);self.assertIsNone(unresolved[0]["attempts"])

    def test_actual_export_row_structure_matches_official_schema(self):
        import sys
        repo=Path(__file__).resolve().parents[2]
        if not (repo/"tools/experiment_protocol.py").is_file():
            repo=Path("/workspace/classical-ecdlp-validation-ready")
        sys.path.insert(0,str(repo/"tools"))
        import experiment_protocol as ep
        schema=ep.read_json(ep.SCHEMAS["experiment.export/v1"])
        # This is a schema-only fixture; it does not represent a scientific run.
        children=[child_panel("shared","rho_reference","f0",0)]
        provider={"app_id":"ap-SYNTHETIC","sandbox_id":"sb-SYNTHETIC","image_id":"im-SYNTHETIC"}
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);child=children[0];path=root/child["execution"];path.parent.mkdir(parents=True);path.write_text("{}")
            child["metadata"]={"status":"native_nonzero","exitcode":3,"provider_identity":provider,"solver_seed":1,
                               "rusage":{},"clock":{},"host_before":{}}
            rows,_,_=e.execution_rows(children,root,{child["execution"]:{"path":child["execution"]}},provider,root)
            import jsonschema
            row_schema={"$schema":schema["$schema"],"$defs":schema["$defs"],**schema["properties"]["runs"]["items"]}
            jsonschema.Draft202012Validator(row_schema).validate(rows[0])
            self.assertEqual(rows[0]["status"],"failed");self.assertEqual(rows[0]["outcome_class"],"completed")
            # A reaped native failure can leave a known-empty stream. Unknown
            # counter costs stay absent rather than a crash or invented zero.
            child["analysis"]=a.summarize_stream([],["q"+str(i) for i in range(64)],
                (child["cell_id"],child["fixture_id"],child["replicate"],child["arm"]))
            rows,_,_=e.execution_rows(children,root,{child["execution"]:{"path":child["execution"]}},provider,root)
            jsonschema.Draft202012Validator(row_schema).validate(rows[0])
            self.assertNotIn("observed_full_native_group_additions",rows[0]["measurements"]["counted"])
            self.assertNotIn("full_native_group_additions_m64",rows[0]["measurements"]["counted"])
            self.assertIsNone(rows[0]["measurements"]["cpu_user_seconds"])

    def test_native_nonzero_remains_completed_process_failed_status(self):
        self.assertEqual(e.row_status({"status":"native_nonzero","exitcode":3},[]),"failed")
        self.assertEqual(e.row_status({"status":"timed_out"},[]),"timeout")


if __name__=="__main__":
    unittest.main()
