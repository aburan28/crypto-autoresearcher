"""Serialize source hashes and original specification fields; no worksheet run."""
from pathlib import Path
import hashlib
import json

import yaml

TASK=Path(__file__).resolve().parent
ROOT=TASK.parents[2]
IDS=("080496","4a3f03","5a293e","6491b4","65f903","911c16")
METHODS={
"080496": ["z-first projective chart census; Fermat normalization", "x-first projective chart census; inverse search", "independent nonzero homogeneous-triple enumeration and scaling quotient"],
"4a3f03": ["x-outer affine census and explicit beta-map orbit walks", "y-outer census and cubic-fibre/sign partitions", "independent square-root table and equivalence closures"],
"5a293e": ["x-outer affine listing and canonical modular coordinate maps", "y-outer affine listing and canonical modular coordinate maps", "independent residue-indexed square-root listing and pointwise coordinate transforms"],
"6491b4": ["Fraction arithmetic including P*T", "Euclidean rational reduction and integer cross comparisons", "independent math.gcd normalization and integer determinants"],
"65f903": ["Fraction ordering and direct powers", "cross multiplication and repeated products", "independent signed determinants and product lists"],
"911c16": ["Fraction coefficient cancellation and numeric substitution", "Euclidean rational pairs and cross multiplication", "independent math.gcd-normalized coefficient determinants"]}
NOTES={
"080496": ["The tail (0:1:0) is explicitly tested; the code records its residual/nonmembership rather than inserting it.", "chart_size_before_normalize counts accepted chart representatives; chart_candidates_tested counts all p^2+p+1 tested projective representatives.", "No group law or translation claim is implemented."],
"4a3f03": ["The linked hypothesis supplies y^2=x^3+B, A=0, and the p7 beta action. The smallest nontrivial cube root is a derived deterministic orbit generator; all nontrivial roots are recorded.", "The affine census is the full nonidentity domain, not a nonzero-x filter. F7 embedding degree is null for the exact noncoprime obstruction, with a residue witness; F13 checks all lower positive exponents through the first1.", "Inputs field7.denominator_mod and field13.denominator_mod have no formula stated in this frozen specification/hypothesis. They remain preserved declared inputs, not claimed measured/verified outputs. This blocks a claim about those two numbers only, not the stated acceptance metrics."],
"5a293e": ["Both x+1 map values are reduced modulo p; witnesses retain pointwise values so invariance alone cannot hide an un-reduced map.", "The zero-y tail control checks complete retention of all roots, without turning an anticipated count into an independent validity requirement."],
"6491b4": ["No success sampling or generic-group experiment is implemented.", "A mismatch with a reduced predicted fraction remains a prediction comparison, not a checker failure."],
"65f903": ["Both explicit tail products5*6 and6*5 are recorded, in addition to the comparison cross products.", "No character sum, corpus key-family census or spectral norm is implemented."],
"911c16": ["Symbolic cancellation uses the same nonzero monomial M*b on both sides for positive inputs; the written identity is a derivation, not a formal proof.", "The only scientific numeric point proposed is the original M16,b4. A distinct M3,b2 coprime fixture is a software-only regression control, not an additional scientific trial.", "No character sum, coordinate-fibre theorem or nonempty-frequency certificate is implemented."]}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_once(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True)+"\n")

for suffix in IDS:
    experiment="EXP-ECDLP-"+suffix
    spec_path=ROOT/"experiments"/experiment/"specification.yaml"
    spec=yaml.safe_load(spec_path.read_text())["experiment"]
    implementation=spec_path.parent/"implementation"
    sources=[TASK/"worksheet_envelope.py",*sorted(implementation.glob("*.py"))]
    if suffix in ("4a3f03","911c16"):
        sources.append(ROOT/"ledger/hypotheses"/(spec["hypothesis_id"]+".yaml"))
    closure={str(p.relative_to(ROOT)):sha(p) for p in sources}
    trials=[]
    for index,route in enumerate(("a","b")):
        impl_path=str(implementation.relative_to(ROOT))
        argv=["/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",impl_path+"/run.py",
              "--route",route,"--trial-plan","<COORDINATOR_FROZEN_NATIVE_PLAN_PATH>","--run-dir","{run_dir}"]
        check=[*argv]; check[1]=impl_path+"/check.py"
        trials.append(dict(trial_id_placeholder="<ALLOCATE_TRIAL_"+route.upper()+">",
            run_id_placeholder="<ALLOCATE_NEW_NATIVE_RUN_"+route.upper()+">",route=route,
            method=METHODS[suffix][index],argv=argv,check_argv=check,
            comparison_trial_id=None if route=="a" else "<ALLOCATE_TRIAL_A>",
            depends_on=[] if route=="a" else ["<ALLOCATE_TRIAL_A>"],
            artifacts=["manifest.yaml","raw-result.json","certificate.yaml"],
            memory_mb_proposed=1024,watchdog_seconds_proposed=120,
            watchdog_reason="Prospective machine-protection ceiling for fixed finite arithmetic/counting plus independent transcript checks; not a research budget."))
    layout=dict(schema="finite-worksheet-prospective-layout/v1",implementation_task="TASK-20261018-993753",
        experiment_id=experiment,official_state_unchanged=True,execution_authorized=False,
        status="source_preparation_not_a_frozen_or_admitted_trial_plan",scientific_trials_executed=0,
        specification=str(spec_path.relative_to(ROOT)),specification_sha256=sha(spec_path),source_sha256=closure,
        original_inputs=spec["inputs"],original_controls=spec["controls"],original_metrics=spec["metrics"],
        original_tail_checks=spec["tail_checks"],original_replication=spec["replication"],
        original_stopping_rules=spec["stopping_rules"],original_invalidation_rules=spec["invalidation_rules"],
        original_success_criterion=spec["success_criterion"],original_falsification_criterion=spec["falsification_criterion"],
        original_required_artifacts=spec["required_artifacts"],original_out_of_scope=spec["out_of_scope"],
        proposed_trials=trials,independent_checker_method=METHODS[suffix][2],
        comparison_policy="Routea records implementations_agree:null while awaiting its separately allocated routeb run. Routeb compares both complete measurements AND canonical witness/point sets against routea, requiring its successful native dependency receipt and unchanged artifact hashes.",
        measurement_policy="Record the computed values and controls. Prediction comparison may be false while control-valid measurement and checker integrity remain true. No hypothesis verdict.",
        seed=None,seed_semantics="No randomness in original worksheet; no invented seed0",curve_id=None,
        outer_certificate=dict(kind="none",verified=None,verifier=None),
        witness_boundary="certificate.yaml is a finite worksheet transcript with a raw-result digest, never a formal proof, decomposition or ECDLP certificate.",
        supervisor_generated_artifacts=["launch.json","execution-receipt.json","command.txt","environment.json","stdout.log","stderr.log","check.stdout.log","check.stderr.log"],
        source_independence="Neither scientific route imports the other or the oracle; oracle independently enumerates/recomputes. Shared helper handles metadata/provenance/output only.",
        notes_and_bounded_ambiguities=NOTES[suffix],
        remaining_admission_obligations=["Coordinator allocates exact random-suffix trial/run IDs and canonical plan/queue/handoff/archive scopes including GENERATED8 plus all3 driver artifacts per run.",
            "Coordinator commits/pushes source closure, resolves requested runtime binding and obtains exact native preapproval/ready authority before delegating actual trials.",
            "The native manifest gate accepts deterministic seed:null. The separate JSON run-manifest schema currently requires an integer seed; this known mismatch is disclosed, not bypassed or repaired here.",
            "No actual frozen cell, route agreement, prediction match, execution-proof closure or official scientific transition has been established by implementation tests."])
    write_once(TASK/"preparation"/experiment/"trial-layout.json",layout)
print("Wrote six prospective source-bound layouts; no scientific computation executed.")
